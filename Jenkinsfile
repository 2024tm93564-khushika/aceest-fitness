pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "2024tm93564/aceest-fitness"
        IMAGE_TAG = "v1.1-ci" 
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo 'Running Pytest...'
                sh 'pip install --break-system-packages -r requirements.txt'
                sh 'python -m pytest'
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                echo 'Pipeline connection established. SonarQube scanner will be integrated in the next release.'
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                echo 'Building Image...'
                sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} ."
                echo 'Pushing to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Updating Kubernetes deployment via pipeline...'
                sh "kubectl set image deployment/aceest-fitness-deployment aceest-fitness-container=${DOCKER_IMAGE}:${IMAGE_TAG}"
                sh "kubectl rollout status deployment/aceest-fitness-deployment"
            }
        }
    }
}