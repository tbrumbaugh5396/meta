pipeline {
    agent any
    
    environment {
        META_ENV = "${env.BRANCH_NAME == 'main' ? 'prod' : 'staging'}"
        META_MANIFESTS_DIR = "manifests"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install -e .
                '''
            }
        }
        
        stage('Validate') {
            steps {
                sh '''
                    . venv/bin/activate
                    meta validate --env ${META_ENV}
                '''
            }
        }
        
        stage('Lock') {
            steps {
                sh '''
                    . venv/bin/activate
                    meta lock --env ${META_ENV}
                '''
            }
        }
        
        stage('Apply') {
            steps {
                sh '''
                    . venv/bin/activate
                    meta apply --env ${META_ENV} --locked --parallel --jobs 4
                '''
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    meta test --env ${META_ENV}
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    meta health --all --env ${META_ENV}
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'manifests/components.lock.*.yaml', fingerprint: true
        }
        failure {
            sh '''
                . venv/bin/activate
                meta health --all --env ${META_ENV} || true
            '''
        }
    }
}


