pipeline {
    agent any

    environment {
        APP_NAME   = 'aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        stage('Environment Setup') {
            steps {
                echo "Setting up Python virtual environment..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "Running flake8 lint check..."
                sh '''
                    . venv/bin/activate
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo "Running pytest suite..."
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v --tb=short --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image..."
                sh "docker build -t ${APP_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${APP_NAME}:${IMAGE_TAG} ${APP_NAME}:latest"
            }
        }

        stage('Docker Test') {
            steps {
                echo "Running pytest inside Docker container..."
                sh """
                    docker run --rm \
                        -v "\$(pwd)/tests:/app/tests" \
                        ${APP_NAME}:latest \
                        python -m pytest tests/ -v --tb=short
                """
            }
        }

    }

    post {
        success {
            echo "BUILD SUCCESSFUL — ${APP_NAME}:${IMAGE_TAG} is ready."
        }
        failure {
            echo "BUILD FAILED — check the console output above."
        }
        always {
            // Clean up dangling images to save disk space
            sh "docker image prune -f || true"
        }
    }
}
