pipeline {
    agent any

    // Build is started by the GitHub webhook (push event)
    triggers {
        githubPush()
    }

    stages {
        stage('Build') {
            steps {
                // Repo is already checked out by "Pipeline script from SCM"
                sh 'docker compose down'
                sh 'docker compose up -d'

                // Smoke test: wait until the API answers (max ~60s)
                sh '''
                    for i in $(seq 1 30); do
                        if curl -sf "http://localhost:5000/predict?x1=2&x2=3&x3=1"; then
                            echo ""
                            echo "API is UP"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "API did not come up"
                    docker compose logs
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose ps'
        }
    }
}
