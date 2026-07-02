pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    cd model
                    python3 -m venv venv
                    venv/bin/pip install --upgrade pip
                    venv/bin/pip install pandas numpy scikit-learn matplotlib joblib
                '''
            }
        }

        stage('Run Model Training') {
            steps {
                echo 'Training the anomaly detection model...'
                sh '''
                    cd model
                    venv/bin/python3 train_model.py
                '''
            }
        }    
        stage('Verify Output') {
            steps {
                echo 'Checking that predictions.csv was generated...'
                sh '''
                    cd model
                    test -f predictions.csv && echo "SUCCESS: predictions.csv generated" || (echo "FAILURE: predictions.csv missing" && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs above.'
        }
    }
}
