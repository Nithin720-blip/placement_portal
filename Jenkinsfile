pipeline {
    agent any

    environment {
        // REPLACE 'your_dockerhub_username' with your actual Docker Hub username in the exam
        DOCKER_IMAGE = 'your_dockerhub_username/placement-portal'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials' // ID of credentials set up in Jenkins
    }

    stages {
        stage('Git Version & Info') {
            steps {
                echo '--- Stage 1: Git Version & Check ---'
                // For Windows Jenkins runners use 'bat', for Linux use 'sh'
                bat 'git --version'
                bat 'git log -n 1 --oneline'
            }
        }

        stage('Dependency Check') {
            steps {
                echo '--- Stage 2: Auditing Dependencies ---'
                bat 'pip install pip-audit'
                bat 'pip-audit -r requirements.txt'
            }
        }

        stage('Code Quality Check') {
            steps {
                echo '--- Stage 3: Code Linting ---'
                bat 'pip install flake8'
                // E9, F63, F7, F82 check syntax errors and undefined names
                bat 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
            }
        }

        stage('Unit Testing') {
            steps {
                echo '--- Stage 4: Running Unit Tests ---'
                bat 'pip install pytest httpx'
                bat 'pytest test_main.py'
            }
        }

        stage('Containerization (Docker Build)') {
            steps {
                echo '--- Stage 5: Building Docker Image ---'
                bat "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest ."
            }
        }

        stage('Hosting Image (Docker Push)') {
            steps {
                echo '--- Stage 6: Pushing to Docker Hub ---'
                // This retrieves the username and password securely from Jenkins Credentials Manager
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                    bat "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    bat "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Deployment') {
            steps {
                echo '--- Stage 7: Deploying via Docker Compose ---'
                bat 'docker-compose down'
                bat 'docker-compose up -d --build'
                echo 'Application deployed successfully at http://localhost:8000'
            }
        }
    }

    post {
        always {
            echo 'Pipeline run completed.'
            cleanWs() // Clean up workspace files
        }
        success {
            echo 'SUCCESS: Pipeline finished successfully!'
        }
        failure {
            echo 'FAILURE: Pipeline failed. Please check the logs above.'
        }
    }
}
