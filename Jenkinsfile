pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_HOST = 'tcp://host.docker.internal:2375'
        VERSION     = "1.0.${BUILD_NUMBER}"
        IMAGE       = "optcg-deckbuilder:1.0.${BUILD_NUMBER}"
        STAGING_URL = 'http://host.docker.internal:3101'
        PROD_URL    = 'http://host.docker.internal:3100'
    }

    stages {

        stage('Build') {
            steps {
                sh '''
                    docker build --target production \
                        -t $IMAGE -t optcg-deckbuilder:latest \
                        --label org.opencontainers.image.version=$VERSION \
                        --label org.opencontainers.image.revision=$GIT_COMMIT \
                        .
                    docker image ls optcg-deckbuilder
                '''
                script {
                    def imageId = sh(script: "docker image inspect ${env.IMAGE} --format '{{.Id}}'", returnStdout: true).trim()
                    writeFile file: 'build-info.json', text: """{
  "version": "${env.VERSION}",
  "image": "${env.IMAGE}",
  "imageId": "${imageId}",
  "commit": "${env.GIT_COMMIT}",
  "build": "${env.BUILD_NUMBER}"
}
"""
                }
                archiveArtifacts artifacts: 'build-info.json', fingerprint: true
            }
        }

        stage('Test') {
            steps {
                sh '''
                    mkdir -p reports
                    docker build --target test -t optcg-deckbuilder:test .
                    docker rm -f optcg-test || true
                    docker run --name optcg-test optcg-deckbuilder:test
                '''
            }
            post {
                always {
                    sh '''
                        rm -rf reports coverage.xml
                        docker cp optcg-test:/app/reports ./reports || true
                        docker cp optcg-test:/app/coverage.xml ./coverage.xml || true
                        docker rm -f optcg-test || true
                    '''
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Code Quality') {
            steps {
                withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        rm -rf sonar-scanner sonar-scanner-cli.zip
                        curl -sSLo sonar-scanner-cli.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-8.1.0.6389-linux-x64.zip
                        unzip -q sonar-scanner-cli.zip
                        mv sonar-scanner-8.1.0.6389-linux-x64 sonar-scanner
                        ./sonar-scanner/bin/sonar-scanner \
                            -Dsonar.token=$SONAR_TOKEN \
                            -Dsonar.projectVersion=$VERSION
                    '''
                }
            }
        }

        stage('Security') {
            steps {
                sh '''
                    mkdir -p reports

                    # 1) Dependency scan (pip-audit) - known CVEs in Python packages
                    docker run --rm optcg-deckbuilder:test \
                        sh -c "pip install --quiet pip-audit && pip-audit -r requirements.txt --format json" \
                        > reports/pip-audit.json || true
                    docker run --rm optcg-deckbuilder:test \
                        sh -c "pip install --quiet pip-audit && pip-audit -r requirements.txt"

                    # 2) Static security analysis (Bandit) - insecure code patterns
                    docker run --rm optcg-deckbuilder:test \
                        sh -c "pip install --quiet bandit && bandit -r app -f txt" \
                        | tee reports/bandit.txt

                    # 3) Container image scan (Trivy) - OS packages + libraries inside the image
                    docker run --rm -v trivy-cache:/root/.cache/ aquasec/trivy:latest image \
                        --docker-host tcp://host.docker.internal:2375 \
                        --scanners vuln --severity HIGH,CRITICAL \
                        $IMAGE | tee reports/trivy-image.txt

                    # Gate: fail only on CRITICAL vulnerabilities that already have a fix
                    docker run --rm -v trivy-cache:/root/.cache/ aquasec/trivy:latest image \
                        --docker-host tcp://host.docker.internal:2375 \
                        --scanners vuln --severity CRITICAL --ignore-unfixed --exit-code 1 --quiet \
                        $IMAGE
                '''
            }
        }

        stage('Deploy (Staging)') {
            steps {
                sh '''
                    export IMAGE_TAG=$VERSION APP_VERSION=$VERSION HOST_PORT=3101 ENV_FILE=./config/staging.env
                    docker compose -p optcg-staging up -d --force-recreate --wait
                    docker compose -p optcg-staging ps
                    sh scripts/smoke-test.sh $STAGING_URL
                '''
            }
        }

        stage('Release (Production)') {
            steps {
                sh '''
                    export APP_VERSION=$VERSION HOST_PORT=3100 ENV_FILE=./config/production.env IMAGE_TAG=prod

                    if docker image inspect optcg-deckbuilder:prod > /dev/null 2>&1; then
                        docker tag optcg-deckbuilder:prod optcg-deckbuilder:prod-previous
                    fi

                    docker tag $IMAGE optcg-deckbuilder:prod

                    if docker compose -p optcg-prod up -d --force-recreate --wait \
                       && sh scripts/smoke-test.sh $PROD_URL; then
                        echo "Release v$VERSION is live in production"
                    else
                        echo "Release failed - rolling back to previous production image"
                        if docker image inspect optcg-deckbuilder:prod-previous > /dev/null 2>&1; then
                            docker tag optcg-deckbuilder:prod-previous optcg-deckbuilder:prod
                            APP_VERSION=previous docker compose -p optcg-prod up -d --force-recreate
                        fi
                        exit 1
                    fi
                '''
                withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GH_USER', passwordVariable: 'GH_TOKEN')]) {
                    sh '''
                        git -c user.name="Jenkins" -c user.email="jenkins@localhost" \
                            tag -a v$VERSION -m "Release v$VERSION (Jenkins build $BUILD_NUMBER)"
                        REPO=${GIT_URL#https://}
                        git push https://$GH_USER:$GH_TOKEN@$REPO v$VERSION
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success {
            echo "Pipeline OK - v${VERSION} deployed to staging (3101) and production (3100)"
        }
        failure {
            echo "Pipeline FAILED at build ${BUILD_NUMBER} - check the stage logs above"
        }
    }
}
