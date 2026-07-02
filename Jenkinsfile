pipeline {
    agent any

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

        stage('Verify Output') {
            steps {
                echo 'Verifying predictions.csv was generated...'
                sh 'test -f model/predictions.csv && echo "SUCCESS: predictions.csv exists" || (echo "FAILURE: missing output" && exit 1)'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}

