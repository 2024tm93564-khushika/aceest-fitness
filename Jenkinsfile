pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "2024tm93564/aceest-fitness"
        IMAGE_TAG = "v3.1.2" 
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
                sh 'pip3 install --break-system-packages -r requirements.txt'
                sh 'python3 -m pytest'
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

        stage('Prepare for Kubernetes Deployment') {
            steps {
                echo 'Image successfully pushed to registry.'
                echo 'In an enterprise environment, Jenkins would now use a Service Account Token to trigger the Kubernetes API.'
                echo 'For this local architecture, execute the deployment rollout from the host machine.'
            }
        }
    }
}