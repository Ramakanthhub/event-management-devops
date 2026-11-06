
import os
import sqlite3
from flask import (
    Flask, request, redirect, session,
    render_template_string, flash, url_for
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "event-devops-secret")
DB = os.environ.get("DB_PATH", "events.db")


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def db():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# --------------------------------------------------
# DATABASE INITIALIZATION AND DUPLICATE FIX
# --------------------------------------------------

def init_db():

    with db() as c:

        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            venue TEXT NOT NULL,
            event_date TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_id INTEGER,
            UNIQUE(user_id, event_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        """)

        # Remove existing duplicate events while preserving
        # registrations belonging to those duplicate events.

        duplicate_groups = c.execute("""
            SELECT title, venue, event_date,
                   COALESCE(description, '') AS description
            FROM events
            GROUP BY title, venue, event_date,
                     COALESCE(description, '')
            HAVING COUNT(*) > 1
        """).fetchall()

        for group in duplicate_groups:

            duplicates = c.execute("""
                SELECT id FROM events
                WHERE title IS ?
                  AND venue IS ?
                  AND event_date IS ?
                  AND COALESCE(description, '') = ?
                ORDER BY id
            """, (
                group["title"],
                group["venue"],
                group["event_date"],
                group["description"]
            )).fetchall()

            keep_id = duplicates[0]["id"]

            for duplicate in duplicates[1:]:
                duplicate_id = duplicate["id"]

                # Transfer registrations to the original event.
                c.execute("""
                    INSERT OR IGNORE INTO registrations
                    (user_id, event_id)
                    SELECT user_id, ?
                    FROM registrations
                    WHERE event_id = ?
                """, (keep_id, duplicate_id))

                # Remove old registrations and duplicate event.
                c.execute(
                    "DELETE FROM registrations WHERE event_id = ?",
                    (duplicate_id,)
                )

                c.execute(
                    "DELETE FROM events WHERE id = ?",
                    (duplicate_id,)
                )

        # Permanent protection against future duplicates.
        c.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_event_details
            ON events (
                title,
                venue,
                event_date,
                COALESCE(description, '')
            )
        """)

        # Insert default event only once.
        c.execute("""
            INSERT OR IGNORE INTO events
            (title, venue, event_date, description)
            VALUES (?, ?, ?, ?)
        """, (
            "Hyderabad Tech Fest",
            "VJIT Campus",
            "2026-12-15",
            "Technology talks and student projects"
        ))

        c.commit()


# --------------------------------------------------
# PROFESSIONAL WEBSITE DESIGN
# --------------------------------------------------

PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{{ title }} | EventHub</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #172033;
        }

        header {
            background: linear-gradient(120deg, #142f50, #205b91);
            color: white;
            padding: 24px 6%;
        }

        header h1 {
            margin: 0 0 18px;
            font-size: 27px;
        }

        nav {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        nav a {
            color: white;
            background: #2879b9;
            text-decoration: none;
            padding: 11px 17px;
            border-radius: 7px;
            font-size: 15px;
            transition: 0.2s;
        }

        nav a:hover {
            background: #3e99dd;
        }

        .container {
            max-width: 1100px;
            margin: 38px auto;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.06);
        }

        h2 {
            color: #183b66;
            margin-top: 0;
        }

        .subtitle {
            color: #69778a;
            margin-bottom: 25px;
        }

        .message {
            background: #e8f7ed;
            color: #16743b;
            padding: 13px;
            border-radius: 7px;
            margin: 12px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 22px;
        }

        th {
            background: #edf3fa;
            color: #183b66;
        }

        th, td {
            padding: 15px;
            border-bottom: 1px solid #e3e8ef;
            text-align: left;
        }

        tr:hover {
            background: #f8fbff;
        }

        .btn {
            display: inline-block;
            background: #176db0;
            color: white;
            padding: 11px 17px;
            border: none;
            border-radius: 7px;
            text-decoration: none;
            cursor: pointer;
            font-size: 14px;
        }

        .btn:hover {
            background: #105487;
        }

        .form-box {
            max-width: 480px;
            margin: 20px auto;
        }

        input {
            width: 100%;
            padding: 13px;
            margin: 9px 0;
            border: 1px solid #d4dce7;
            border-radius: 7px;
            font-size: 15px;
        }

        input:focus {
            outline: 2px solid #9bc9ef;
        }

        .empty {
            text-align: center;
            padding: 30px;
            color: #78869a;
        }

        footer {
            text-align: center;
            color: #8290a2;
            padding: 25px;
        }

        @media(max-width: 700px) {
            .container {
                margin: 18px 12px;
                padding: 18px;
                overflow-x: auto;
            }

            header {
                padding: 20px;
            }

            header h1 {
                font-size: 21px;
            }

            th, td {
                padding: 10px;
                font-size: 13px;
            }
        }
    </style>
</head>

<body>

<header>
    <h1>EventHub | Online Event Registration</h1>

    <nav>
        <a href="/">Events</a>
        <a href="/register">Student Registration</a>
        <a href="/login">Login</a>
        <a href="/admin">Admin Dashboard</a>
        <a href="/logout">Logout</a>
    </nav>
</header>

<div class="container">

    <h2>{{ title }}</h2>

    {% if session.get('name') %}
        <p class="subtitle">
            Welcome, {{ session.get('name') }}!
        </p>
    {% endif %}

    {% with messages = get_flashed_messages() %}
        {% for message in messages %}
            <div class="message">{{ message }}</div>
        {% endfor %}
    {% endwith %}

    {{ content | safe }}

</div>

<footer>
    EventHub - Student Event Management System
    <br>
    Built with Flask, SQLite and DevOps tools
</footer>

</body>
</html>
"""


def page(title, content):
    return render_template_string(
        PAGE,
        title=title,
        content=content
    )


# --------------------------------------------------
# HEALTH CHECK - DOCKER AND JENKINS
# --------------------------------------------------

@app.route("/health")
def health():
    return {"status": "ok", "application": "EventHub"}, 200


# --------------------------------------------------
# HOME - EVENT LISTING
# --------------------------------------------------

@app.route("/")
def events():

    with db() as c:
        rows = c.execute("""
            SELECT * FROM events
            ORDER BY event_date, title
        """).fetchall()

    content = render_template_string("""
        <p class="subtitle">
            Discover upcoming college events and register online.
        </p>

        {% if rows %}

        <table>
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Venue</th>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Action</th>
                </tr>
            </thead>

            <tbody>
                {% for event in rows %}
                <tr>
                    <td><strong>{{ event.title }}</strong></td>
                    <td>{{ event.venue }}</td>
                    <td>{{ event.event_date }}</td>
                    <td>{{ event.description or '' }}</td>
                    <td>
                        <a class="btn"
                           href="{{ url_for('book', event_id=event.id) }}">
                           Register
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        {% else %}
            <div class="empty">No events available currently.</div>
        {% endif %}
    """, rows=rows)

    return page("Available Events", content)


# --------------------------------------------------
# STUDENT REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please complete all fields.")
            return redirect("/register")

        try:
            with db() as c:
                c.execute("""
                    INSERT INTO users(name, email, password)
                    VALUES (?, ?, ?)
                """, (name, email, password))

            flash("Registration successful. Please log in.")
            return redirect("/login")

        except sqlite3.IntegrityError:
            flash("Email already registered.")
            return redirect("/register")

    content = """
        <div class="form-box">
            <p class="subtitle">
                Create your student account to register for events.
            </p>

            <form method="POST">
                <input name="name"
                       placeholder="Full Name"
                       required>

                <input name="email"
                       type="email"
                       placeholder="Email Address"
                       required>

                <input name="password"
                       type="password"
                       placeholder="Password"
                       required>

                <button class="btn" type="submit">
                    Create Account
                </button>
            </form>
        </div>
    """

    return page("Student Registration", content)


# --------------------------------------------------
# STUDENT LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with db() as c:
            user = c.execute("""
                SELECT * FROM users
                WHERE email = ? AND password = ?
            """, (email, password)).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["name"] = user["name"]

            flash("Login successful.")
            return redirect("/")

        flash("Invalid login details.")
        return redirect("/login")

    content = """
        <div class="form-box">

            <p class="subtitle">
                Login to register for your favourite events.
            </p>

            <form method="POST">

                <input name="email"
                       type="email"
                       placeholder="Email Address"
                       required>

                <input name="password"
                       type="password"
                       placeholder="Password"
                       required>

                <button class="btn" type="submit">
                    Login
                </button>

            </form>
        </div>
    """

    return page("Student Login", content)


# --------------------------------------------------
# EVENT REGISTRATION
# --------------------------------------------------

@app.route("/book/<int:event_id>")
def book(event_id):

    if not session.get("user_id"):
        flash("Please log in before registering.")
        return redirect("/login")

    with db() as c:

        event = c.execute(
            "SELECT id FROM events WHERE id = ?",
            (event_id,)
        ).fetchone()

        if not event:
            flash("Event not found.")
            return redirect("/")

        try:
            c.execute("""
                INSERT INTO registrations(user_id, event_id)
                VALUES (?, ?)
            """, (session["user_id"], event_id))

            c.commit()
            flash("Event registration confirmed!")

        except sqlite3.IntegrityError:
            flash("You are already registered for this event.")

    return redirect("/")


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin")
def admin():

    with db() as c:

        rows = c.execute("""
            SELECT
                u.name,
                u.email,
                e.title,
                e.venue,
                e.event_date
            FROM registrations r
            JOIN users u ON u.id = r.user_id
            JOIN events e ON e.id = r.event_id
            ORDER BY e.event_date
        """).fetchall()

        event_count = c.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        student_count = c.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        registration_count = c.execute(
            "SELECT COUNT(*) FROM registrations"
        ).fetchone()[0]

    content = render_template_string("""
        <p class="subtitle">
            Overview of events and student registrations.
        </p>

        <h3>Total Events: {{ event_count }}</h3>
        <h3>Total Students: {{ student_count }}</h3>
        <h3>Total Registrations: {{ registration_count }}</h3>

        <h3>Registered Participants</h3>

        {% if rows %}

        <table>
            <thead>
                <tr>
                    <th>Student</th>
                    <th>Email</th>
                    <th>Event</th>
                    <th>Venue</th>
                    <th>Date</th>
                </tr>
            </thead>

            <tbody>
                {% for r in rows %}
                <tr>
                    <td>{{ r.name }}</td>
                    <td>{{ r.email }}</td>
                    <td>{{ r.title }}</td>
                    <td>{{ r.venue }}</td>
                    <td>{{ r.event_date }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        {% else %}
            <div class="empty">
                No participants registered yet.
            </div>
        {% endif %}
    """,
        rows=rows,
        event_count=event_count,
        student_count=student_count,
        registration_count=registration_count
    )

    return page("Admin Dashboard", content)


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect("/")


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
