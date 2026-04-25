pipeline {
    agent any

    environment {
        APP_NAME   = 'aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        DOCKERHUB_IMAGE = 'akshaya45/aceest-app'
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
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "Running flake8 lint check..."
                bat '''
                    call venv\\Scripts\\activate.bat
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    bat """
                        sonar-scanner ^
                        -Dsonar.projectKey=aceest-fitness ^
                        -Dsonar.sources=. ^
                        -Dsonar.host.url=http://host.docker.internal:9000 ^
                        -Dsonar.token=squ_bc6bbb3827287ef6d90a30ca4e0e3a471c30d5c4
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Unit Tests') {
            steps {
                echo "Running pytest suite..."
                bat '''
                    call venv\\Scripts\\activate.bat
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
                bat "docker build -t %APP_NAME%:%IMAGE_TAG% ."
                bat "docker tag %APP_NAME%:%IMAGE_TAG% %APP_NAME%:latest"
                bat "docker tag %APP_NAME%:%IMAGE_TAG% %DOCKERHUB_IMAGE%:%IMAGE_TAG%"
                bat "docker tag %APP_NAME%:%IMAGE_TAG% %DOCKERHUB_IMAGE%:latest"
            }
        }

        stage('Docker Push') {
            steps {
                echo "Pushing image to Docker Hub..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                    bat "docker push %DOCKERHUB_IMAGE%:%IMAGE_TAG%"
                    bat "docker push %DOCKERHUB_IMAGE%:latest"
                }
            }
        }

        stage('Docker Test') {
            steps {
                echo "Running pytest inside Docker container..."
                bat "docker run --rm -v \"%CD%/tests:/app/tests\" %APP_NAME%:latest python -m pytest tests/ -v --tb=short"
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
            bat "docker image prune -f"
        }
    }
}