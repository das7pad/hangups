//
// This file is autogenerated.
// To update, run:
//
//    make Jenkinsfile
//

pipeline {
    agent none
    environment {
        GIT_COMMITTER_NAME  = 'Joe Doe'
        GIT_COMMITTER_EMAIL = 'joe.doe@example.com'
        HOME                = '/tmp/'
    }
    options {
        timestamps()
        skipDefaultCheckout(true)
    }
    stages {
        stage('Parallel Stage') {
            parallel {
                stage('Python:3.6.9') {
                    agent {
                        docker {
                            image 'python:3.6.9'
                        }
                    }
                    stages {
                        stage('Python:3.6.9 Info') {
                            steps {
                                sh 'curl -sS httpbin.org/ip'
                                sh 'pwd'
                            }
                        }
                        stage('Python:3.6.9 Checkout') {
                            steps {
                                checkout scm
                                sh 'make clean'
                            }
                        }
                        stage('Python:3.6.9 Install') {
                            steps {
                                sh 'make venv-deps'
                            }
                        }
                        stage('Python:3.6.9 Test') {
                            steps {
                                sh 'make test-all'
                            }
                        }
                        stage('Python:3.6.9 Cleanup') {
                            steps {
                                sh 'make clean'
                            }
                        }
                    }
                }
                stage('Python:3.6.12') {
                    agent {
                        docker {
                            image 'python:3.6.12'
                        }
                    }
                    stages {
                        stage('Python:3.6.12 Info') {
                            steps {
                                sh 'curl -sS httpbin.org/ip'
                                sh 'pwd'
                            }
                        }
                        stage('Python:3.6.12 Checkout') {
                            steps {
                                checkout scm
                                sh 'make clean'
                            }
                        }
                        stage('Python:3.6.12 Install') {
                            steps {
                                sh 'make venv-deps'
                            }
                        }
                        stage('Python:3.6.12 Test') {
                            steps {
                                sh 'make test-all'
                            }
                        }
                        stage('Python:3.6.12 Cleanup') {
                            steps {
                                sh 'make clean'
                            }
                        }
                    }
                }
                stage('Python:3.7.5') {
                    agent {
                        docker {
                            image 'python:3.7.5'
                        }
                    }
                    stages {
                        stage('Python:3.7.5 Info') {
                            steps {
                                sh 'curl -sS httpbin.org/ip'
                                sh 'pwd'
                            }
                        }
                        stage('Python:3.7.5 Checkout') {
                            steps {
                                checkout scm
                                sh 'make clean'
                            }
                        }
                        stage('Python:3.7.5 Install') {
                            steps {
                                sh 'make venv-deps'
                            }
                        }
                        stage('Python:3.7.5 Test') {
                            steps {
                                sh 'make test-all'
                            }
                        }
                        stage('Python:3.7.5 Cleanup') {
                            steps {
                                sh 'make clean'
                            }
                        }
                    }
                }
                stage('Python:3.7.8') {
                    agent {
                        docker {
                            image 'python:3.7.8'
                        }
                    }
                    stages {
                        stage('Python:3.7.8 Info') {
                            steps {
                                sh 'curl -sS httpbin.org/ip'
                                sh 'pwd'
                            }
                        }
                        stage('Python:3.7.8 Checkout') {
                            steps {
                                checkout scm
                                sh 'make clean'
                            }
                        }
                        stage('Python:3.7.8 Install') {
                            steps {
                                sh 'make venv-deps'
                            }
                        }
                        stage('Python:3.7.8 Test') {
                            steps {
                                sh 'make test-all'
                            }
                        }
                        stage('Python:3.7.8 Cleanup') {
                            steps {
                                sh 'make clean'
                            }
                        }
                    }
                }
                stage('Python:3.8.2') {
                    agent {
                        docker {
                            image 'python:3.8.2'
                        }
                    }
                    stages {
                        stage('Python:3.8.2 Info') {
                            steps {
                                sh 'curl -sS httpbin.org/ip'
                                sh 'pwd'
                            }
                        }
                        stage('Python:3.8.2 Checkout') {
                            steps {
                                checkout scm
                                sh 'make clean'
                            }
                        }
                        stage('Python:3.8.2 Install') {
                            steps {
                                sh 'make venv-deps'
                            }
                        }
                        stage('Python:3.8.2 Test') {
                            steps {
                                sh 'make test-all'
                            }
                        }
                        stage('Python:3.8.2 Cleanup') {
                            steps {
                                sh 'make clean'
                            }
                        }
                    }
                }
                stage('Python:3.8.5') {
                    agent {
                        docker {
                            image 'python:3.8.5'
                        }
                    }
                    stages {
                        stage('Python:3.8.5 Info') {
                            steps {
                                sh 'curl -sS httpbin.org/ip'
                                sh 'pwd'
                            }
                        }
                        stage('Python:3.8.5 Checkout') {
                            steps {
                                checkout scm
                                sh 'make clean'
                            }
                        }
                        stage('Python:3.8.5 Install') {
                            steps {
                                sh 'make venv-deps'
                            }
                        }
                        stage('Python:3.8.5 Test') {
                            steps {
                                sh 'make test-all'
                            }
                        }
                        stage('Python:3.8.5 Cleanup') {
                            steps {
                                sh 'make clean'
                            }
                        }
                    }
                }
            }
        }
    }
}