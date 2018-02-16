def axisImages = ['jessie', 'stretch']
def axisPython = ['py27', 'py3']
def axisCherrypy = ['cherrypy35','cherrypy4','cherrypy5','cherrypy6','cherrypy7','cherrypy8','cherrypy9','cherrypy10','cherrypy11','cherrypy12','cherrypy13','cherrypy14']


def builders = [:]
for (x in axisImages) {
for (y in axisPython) {
for (z in axisCherrypy) {
    // Need to bind the label variable before the closure - can't do 'for (label in labels)'
    def image = x 
    def python = y
    def cherrypy = z
    def env = "${python}-${cherrypy}"

    // Create a map to pass in to the 'parallel' step so we can fire all the builds at once
    builders["${image}-${env}"] = {
        node {
            /* Requires the Docker Pipeline plugin to be installed */
            docker.image("ikus060/docker-debian-py2-py3:${image}").inside {
                stage("${image}-${env}:Initialize") {
                    // Wipe working directory to make sure to build clean.
                    deleteDir()
                     // Checkout 
                    checkout scm
                    echo 'Upgrade python and install dependencies to avoid compiling from sources.'
                    sh 'apt-get update && apt-get -qq install python-pysqlite2 libldap2-dev libsasl2-dev rdiff-backup node-less'
                    sh 'pip install pip setuptools tox --upgrade'
                }
                stage("${image}-${env}:Build") {
                    echo 'Compile catalog and less'
                    sh 'python setup.py build'
                }
                stage("${image}-${env}:Test") {
                    try {
                        sh "tox --recreate --workdir /tmp --sitepackages -e ${env}"
                    } finally {
                        junit "nosetests-${env}.xml"
                        step([$class: 'CoberturaPublisher', coberturaReportFile: "coverage-${env}.xml"])
                    }
                }
            }
        }
    }
}}}

parallel builders
    
node {
    stage ('Publish') {
        if (env.BRANCH_NAME == 'master') {
            // Wipe working directory to make sure to build clean.
            deleteDir()
            // Checkout 
            checkout scm
            // Define version
            def pyVersion = sh(
              script: 'python setup.py --version | tail -n1',
              returnStdout: true
            ).trim()
            def version = pyVersion.replaceFirst(".dev.*", ".${BUILD_NUMBER}")
        
            // Push changes to git
            withCredentials([usernamePassword(credentialsId: 'gitlab-jenkins', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                sh """
                  sed -i.bak -r "s/version='(.*).dev.*'/version='${version}'/" setup.py
                  git config --local user.email "jenkins@patrikdufresne.com"
                  git config --local user.name "Jenkins"
                  git commit setup.py -m 'Release ${version}'
                  git tag '${version}'
                  git push http://${GIT_USERNAME}:${GIT_PASSWORD}@git.patrikdufresne.com/pdsl/rdiffweb.git --tags
                """
            }
        
        
            // Publish to pypi
            docker.image("ikus060/docker-debian-py2-py3:jessie").inside {
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'ikus060-pypi', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh """
                    cat > ~/.pypirc << EOF
[distutils]
index-servers =
  pypi

[pypi]
username=${USERNAME}
password=${PASSWORD}   
EOF
                    """
                    writeFile file: "/root/.pypirc", text: """
    
                    """
                    sh 'cat /root/.pypirc'
                    sh 'pip install wheel --upgrade'
                    sh 'python setup.py sdist bdist_wheel upload -r pypi'
                }
            }
        }
        
    }
}