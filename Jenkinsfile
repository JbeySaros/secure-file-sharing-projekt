pipeline {
    agent any
    
    environment {
        // DockerHub credentials
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_REPO = 'jbeysaros23/secure-file-sharing-projekt'
        
        // Application settings
        MASTER_PASSWORD = 'jenkins_test_master_2024'
        API_PASSWORD = 'jenkins_test_api_2024'
        
        // Build info
        BUILD_TIMESTAMP = sh(returnStdout: true, script: 'date +%Y%m%d-%H%M%S').trim()
        IMAGE_TAG = "${BUILD_NUMBER}-${BUILD_TIMESTAMP}"
    }
    
    options {
        // Garder seulement les 10 derniers builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // Timeout global
        timeout(time: 30, unit: 'MINUTES')
        
        // Nettoyer le workspace avant le build
        skipDefaultCheckout(false)
    }
    
    stages {
        stage('🏗️Preparation') {
            steps {
                script {
                    echo " Starting CI/CD Pipeline for Secure File Sharing"
                    echo " Build: ${BUILD_NUMBER}"
                    echo "Tag: ${IMAGE_TAG}"
                    echo " Docker repo: ${DOCKERHUB_REPO}"
                }
                
                // Nettoyer le workspace
                cleanWs()
                
                // Checkout du code
                checkout scm
                
                // Création du venv 
                sh 'ls -la'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                '''
            }
        }
        
        stage(' Code Quality & Security') {
            parallel {
                stage('Lint Code') {
                    steps {
                        script {
                            sh '''
                                . venv/bin/activate
                                pip install flake8
                                
                                echo " Running code linting..."
                                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
                            '''
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        script {
                            sh '''
                                . venv/bin/activate
                                pip install safety bandit
                                
                                echo "Running security scan..."
                                safety check || echo "Safety check completed with warnings"
                                bandit -r . -f json || echo "Bandit scan completed with warnings"
                            '''
                        }
                    }
                }
            }
        }
        
        stage(' Tests') {
            steps {
                script {
                    sh '''
                        echo " Setting up test environment..."
                        . venv/bin/activate
                        pip install -r requirements.txt
                        
                        echo " Running unit tests..."
                        API_PASSWORD=${API_PASSWORD} python -m pytest tests/ -v --tb=short || exit 1
                        
                        echo "✅ Firsts tests passed!"
                    '''
                }
            }
            post {
                always {
                    // Publier les résultats de tests si disponibles
                    script {
                        if (fileExists('test-results.xml')) {
                            junit 'test-results.xml'
                        }
                    }
                }
            }
        }
        
        stage(' Docker Build') {
            steps {
                script {
                    echo " Building Docker image..."
                    
                    // Build de l'image avec plusieurs tags
                    sh """
                        docker build \\
                            --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \\
                            --build-arg VCS_REF=\$(git rev-parse --short HEAD) \\
                            --build-arg BUILD_NUMBER=${BUILD_NUMBER} \\
                            -t ${DOCKERHUB_REPO}:${IMAGE_TAG} \\
                            -t ${DOCKERHUB_REPO}:latest \\
                            -t ${DOCKERHUB_REPO}:build-${BUILD_NUMBER} \\
                            .
                    """
                    
                    // Tester que l'image fonctionne
                    sh """
                        echo " Testing Docker image..."
                        docker run --rm -d --name test-container -p 5001:5000 \\
                            -e MASTER_PASSWORD=${MASTER_PASSWORD} \\
                            -e API_PASSWORD=${API_PASSWORD} \\
                            ${DOCKERHUB_REPO}:${IMAGE_TAG}                        
                            curl -f http://localhost:5000/ && curl -f http://localhost:5000/health
                        
                        # Arrêter le container de test
                        docker stop test-container
                        
                        echo "✅ Docker image test passed!"
                    """
                }
            }
        }
        
        stage('Push to DockerHub') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "Pushing to DockerHub..."

                    withDockerRegistry([credentialsId: 'dockerhub-credentials', url: 'https://index.docker.io/v1/']) {
                        // Push toutes les images taguées
                        docker.image("${DOCKERHUB_REPO}:${IMAGE_TAG}").push()
                        docker.image("${DOCKERHUB_REPO}:latest").push()
                        docker.image("${DOCKERHUB_REPO}:build-${BUILD_NUMBER}").push()
                    }

                    echo "✅ Images pushed successfully!"
                    echo "Available tags:"
                    echo "  - ${DOCKERHUB_REPO}:${IMAGE_TAG}"
                    echo "  - ${DOCKERHUB_REPO}:latest"
                    echo "  - ${DOCKERHUB_REPO}:build-${BUILD_NUMBER}"
                }
            }
        }
            post {
                always {
                    // Logout DockerHub
                    sh 'docker logout'
                }
            }
        }
        
        stage(' Deploy & Integration Tests') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo " Deploying and running integration tests..."
                    
                    sh """
                        # Arrêter les anciens containers
                        docker stop secure-file-api || true
                        docker rm secure-file-api || true
                        
                        # Lancer le nouveau container
                        docker run -d --name secure-file-api \\
                            -p 5002:5000 \\
                            -e MASTER_PASSWORD=${MASTER_PASSWORD} \\
                            -e API_PASSWORD=${API_PASSWORD} \\
                            ${DOCKERHUB_REPO}:${IMAGE_TAG}
                        
                        # Attendre le démarrage
                        sleep 15
                        
                        # Tests d'intégration
                        echo " Running integration tests..."
                        
                        # Test API
                        curl -f http://localhost:5002/ || exit 1
                        curl -f http://localhost:5002/health || exit 1
                        
                        # Test upload/download
                        echo "Integration test file" > integration_test.txt
                        
                        upload_response=\$(curl -s -X POST \\
                            -H "Authorization: Bearer ${API_PASSWORD}" \\
                            -F "file=@integration_test.txt" \\
                            http://localhost:5002/upload)
                        
                        echo "Upload response: \$upload_response"
                        
                        if [[ \$upload_response == *"file_id"* ]]; then
                            echo "✅ Integration tests passed!"
                        else
                            echo "❌ Integration tests failed!"
                            exit 1
                        fi
                        
                        # Nettoyer
                        rm -f integration_test.txt
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Nettoyer les images Docker locales
            script {
                sh """
                    docker system prune -f
                    docker rmi ${DOCKERHUB_REPO}:${IMAGE_TAG} || true
                    docker rmi ${DOCKERHUB_REPO}:latest || true
                """
            }
            
            // Nettoyer le workspace
            cleanWs()
        }
        
        success {
            script {
                echo """
                 Pipeline completed successfully!
                
                Build Summary:
                ├── Build Number: ${BUILD_NUMBER}
                ├── Image Tag: ${IMAGE_TAG}  
                ├── DockerHub: https://hub.docker.com/r/${DOCKERHUB_REPO}
                └── Deployment: http://localhost:5002
                
                 Theapplication build is ready for production!
                """
            }
        }
        
        failure {
            script {
                echo """
                ❌ Pipeline failed!
                
                🔍 Check the logs above for details.
                💡 Common issues:
                ├── Dependencies not installed
                ├── Tests failing  
                ├── Docker build issues
                └── Network connectivity problems
                """
            }
        }
    }
}
