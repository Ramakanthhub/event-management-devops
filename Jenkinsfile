pipeline {
  agent any
  environment {
    IMAGE_NAME = 'devops-practical-app'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Install dependencies') {
      steps {
        sh 'python3 -m venv .venv'
        sh '. .venv/bin/activate && pip install -r requirements.txt'
      }
    }
    stage('Python syntax check') {
      steps { sh '. .venv/bin/activate && python -m py_compile app.py' }
    }
    stage('Build Docker image') {
      steps { sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .' }
    }
    stage('Start application and Selenium') {
      steps { sh 'docker compose up -d --build' }
    }
    stage('Selenium browser tests') {
      steps {
        sh 'sleep 20'
        sh '. .venv/bin/activate && BASE_URL=http://127.0.0.1:5000 SELENIUM_URL=http://127.0.0.1:4444/wd/hub python -m unittest discover -s tests -v'
      }
    }
  }
  post {
    always { sh 'docker compose down -v || true' }
  }
}
