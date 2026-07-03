pipeline {
    agent any

    environment {
        ECR_URI = "732778637529.dkr.ecr.eu-north-1.amazonaws.com/cloud-cost-anomaly-detector"
        AWS_REGION = "eu-north-1"
        IMAGE_TAG = "latest"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Run Model Training') {
            steps {
                echo 'Training the anomaly detection model...'
                sh 'cd model && python3 train_model.py'
            }
        }

        stage('Verify Model Output') {
            steps {
                echo 'Verifying predictions.csv was generated...'
                sh 'test -f model/predictions.csv && echo "SUCCESS: predictions.csv exists" || (echo "FAILURE: missing output" && exit 1)'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t cloud-cost-anomaly-detector:${IMAGE_TAG} -f deployment/Dockerfile .
                '''
            }
        }

        stage('ECR Push') {
            steps {
                echo 'Pushing Docker image to ECR...'
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}
                    docker tag cloud-cost-anomaly-detector:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
                    docker push ${ECR_URI}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying FastAPI container...'
                sh '''
                    docker stop anomaly-api || true
                    docker rm anomaly-api || true
                    docker run -d --name anomaly-api -p 8000:8000 ${ECR_URI}:${IMAGE_TAG}
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed! API is live at http://13.63.166.181:8000'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}
