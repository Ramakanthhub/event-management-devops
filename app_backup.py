from flask import Flask, request, redirect, url_for, session, render_template_string, flash
import sqlite3, os

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","event-devops-secret")
DB=os.environ.get("DB_PATH","events.db")

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,password TEXT);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,title TEXT,venue TEXT,event_date TEXT,description TEXT);
        CREATE TABLE IF NOT EXISTS registrations(id INTEGER PRIMARY KEY,user_id INTEGER,event_id INTEGER,
          UNIQUE(user_id,event_id),FOREIGN KEY(user_id) REFERENCES users(id),FOREIGN KEY(event_id) REFERENCES events(id));
        """)
        c.execute("INSERT OR IGNORE INTO events(title,venue,event_date,description) VALUES(?,?,?,?)",
          ("Hyderabad Tech Fest","VJIT Campus","2026-12-15","Technology talks and student projects"))
        c.commit()

PAGE="""<!doctype html><html><head><title>{{title}}</title><style>
body{font-family:Arial;background:#f3f6fb;margin:0;color:#172033}header{background:#183b66;color:white;padding:18px 5%}
main{max-width:900px;margin:28px auto;background:white;padding:25px;border-radius:10px}
a,button{background:#1769aa;color:white;padding:9px 13px;border:0;border-radius:5px;text-decoration:none;cursor:pointer}
input{padding:9px;margin:5px;border:1px solid #bbb;border-radius:4px}table{width:100%;border-collapse:collapse;margin-top:15px}
td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}.msg{color:#087a3e}
</style></head><body><header><h2>Online Event Registration & Management</h2>
<a href="/">Events</a> <a href="/register">Student Registration</a> <a href="/login">Login</a> <a href="/admin">Admin Dashboard</a> <a href="/logout">Logout</a>
</header><main><h2>{{title}}</h2>{% for m in get_flashed_messages() %}<p class="msg">{{m}}</p>{% endfor %}{{body|safe}}</main></body></html>"""

def page(title,body): return render_template_string(PAGE,title=title,body=body)

@app.route("/health")
def health(): return {"status":"ok"}

@app.route("/")
def events():
    with db() as c: rows=c.execute("SELECT * FROM events ORDER BY event_date").fetchall()
    body="<table><tr><th>Event</th><th>Venue</th><th>Date</th><th>Description</th><th></th></tr>"
    body += "".join(f"<tr><td>{r['title']}</td><td>{r['venue']}</td><td>{r['event_date']}</td><td>{r['description']}</td><td><a href='/book/{r['id']}'>Register</a></td></tr>" for r in rows)
    return page("Available Events",body+"</table>")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            with db() as c:
                c.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                  (request.form["name"],request.form["email"],request.form["password"])); c.commit()
            flash("Registration successful. Please log in."); return redirect("/login")
        except sqlite3.IntegrityError: flash("Email already registered")
    return page("Student Registration","""<form method="post"><input name="name" placeholder="Full name" required>
    <input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Password" required>
    <button>Create Account</button></form>""")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        with db() as c: u=c.execute("SELECT * FROM users WHERE email=? AND password=?",(request.form["email"],request.form["password"])).fetchone()
        if u: session["user_id"]=u["id"]; session["name"]=u["name"]; return redirect("/")
        flash("Invalid login details")
    return page("Student Login","""<form method="post"><input name="email" type="email" placeholder="Email" required>
    <input name="password" type="password" placeholder="Password" required><button>Login</button></form>""")

@app.route("/book/<int:event_id>")
def book(event_id):
    if not session.get("user_id"): flash("Please log in before registering"); return redirect("/login")
    try:
        with db() as c:
            c.execute("INSERT INTO registrations(user_id,event_id) VALUES(?,?)",(session["user_id"],event_id)); c.commit()
        flash("Event registration confirmed")
    except sqlite3.IntegrityError: flash("You are already registered for this event")
    return redirect("/")

@app.route("/admin")
def admin():
    with db() as c:
        rows=c.execute("""SELECT u.name,u.email,e.title,e.event_date FROM registrations r
        JOIN users u ON u.id=r.user_id JOIN events e ON e.id=r.event_id ORDER BY e.event_date""").fetchall()
    body="<table><tr><th>Participant</th><th>Email</th><th>Event</th><th>Date</th></tr>"
    body += "".join(f"<tr><td>{r['name']}</td><td>{r['email']}</td><td>{r['title']}</td><td>{r['event_date']}</td></tr>" for r in rows)
    return page("Admin Dashboard - Registered Participants",body+"</table>")

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

init_db()
if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
