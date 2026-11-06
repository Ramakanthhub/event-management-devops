
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Docker') {
            steps {
                bat 'docker --version'
                bat 'docker compose version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    py -3 -m venv .jenkins-venv
                    .jenkins-venv\\Scripts\\python.exe -m pip install --upgrade pip
                    if exist requirements.txt (
                        .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements.txt
                    ) else (
                        .jenkins-venv\\Scripts\\python.exe -m pip install Flask selenium
                    )
                '''
            }
        }

        stage('Python Syntax Check') {
            steps {
                bat '.jenkins-venv\\Scripts\\python.exe -m py_compile app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t event-management-app:latest .'
            }
        }

        stage('Start Application and Selenium') {
            steps {
                bat 'docker compose up -d --build'

                bat '''
                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddMinutes(2); do { try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/health; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Seconds 3 } while ((Get-Date) -lt $deadline); exit 1"
                '''
            }
        }

        stage('Selenium Browser Tests') {
            steps {
                bat '''
                    set BASE_URL=http://127.0.0.1:5000
                    set SELENIUM_URL=http://127.0.0.1:4444/wd/hub
                    .jenkins-venv\\Scripts\\python.exe -m unittest discover -s tests -v
                '''
            }
        }
    }

    post {
        always {
            bat(returnStatus: true, script: 'docker compose down --remove-orphans')
        }
        success {
            echo 'SUCCESS: Event Management DevOps Pipeline Completed!'
        }
        failure {
            echo 'FAILED: Check Jenkins Console Output.'
        }
    }
}
