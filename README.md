# Event Management

## Demo
- Run locally: `python -m venv .venv` then activate it and run `pip install -r requirements.txt`
- Start: `python app.py`
- Open: http://127.0.0.1:5000
- Health check: http://127.0.0.1:5000/health

## Docker
- Build: `docker build -t event_management:1.0 .`
- Run: `docker run -d --name event_management-container -p 5000:5000 event_management:1.0`
- Stop: `docker stop event_management-container`
- Remove: `docker rm event_management-container`

## Selenium + Docker Compose
- `docker compose up -d --build`
- Install Python packages: `pip install -r requirements.txt`
- Run tests: `python -m unittest discover -s tests -v`
- Stop: `docker compose down -v`

## Demo credentials / data
See the app page. The attendance app has a seeded faculty account: `faculty` / `faculty123`.
The event app seeds one sample event; create a student account before registering.

## GitHub
Create an empty GitHub repository, then:
`git init`
`git add .`
`git commit -m "Initial project commit"`
`git branch -M main`
`git remote add origin https://github.com/YOUR-USERNAME/REPOSITORY.git`
`git push -u origin main`

Configure Jenkins with this repository URL and use `Jenkinsfile` as the pipeline script.
