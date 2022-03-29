pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        echo 'Checking out SCM'
        checkout scm
      }
    }

    stage('Build') {
      steps {
        echo 'In build stage!'
		sh 'python3 setup.py clean'
		sh 'rm -rf dist'
		sh 'python3 setup.py sdist --formats=gztar,zip'
		sh 'pip3 install .'
		sh 'rm -rf docs/_build'
		sh 'cd pre_scripts && /bin/bash build_docs_no_check.sh'
		sh 'rsync -av docs/_build/html/ ~/apache-tomcat-8.5.64/webapps/python-docs/axioma-py'
      }
    }
    stage('Test') {
        steps {
          echo 'In test stage!'
		  sh 'python3 axiomapy/test/unit/apis/test_portfolio_api.py'
		  sh 'python3 axiomapy/test/unit/apis/test_entities_api.py'
		  sh 'python3 axiomapy/test/unit/apis/test_rms_api.py'
          //sh './gradlew check'
      }
    }
    stage('Deploy') {
      steps {
        echo 'In deploy stage!'
		sh 'cp dist/*.zip dist/*.tar.gz ~/pypi-server/packages3/'
      }
    }
  }

  post {
    success {
      echo "Sending Success email"

      emailext body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER} \nMore info at: ${env.BUILD_URL}",
        subject: "Jenkins: ${env.JOB_BASE_NAME} BUILD SUCCESSFUL!",
        to: "bspector@qontigo.com",
        from: "jenkins@qontigo.com"
    }

    failure {
      echo "Sending Failure email"

      emailext body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER} \nMore info at: ${env.BUILD_URL}",
        subject: "Jenkins: ${env.JOB_BASE_NAME} BUILD FAILED!!!!!!",
        to: emailextrecipients([
                         [$class: 'CulpritsRecipientProvider']
                     ]),
        from: "jenkins@qontigo.com"
    }
  }
}
