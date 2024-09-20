def ENV_LOC = [:]
// Which nodes build tools. The linux-x64-tools-conan-center-index is an older machine
// that uses an earlier glibc, so the tools will run on every machine.
def BUILD_TOOLS=[
    'aix-conan-center-index': true,
    'windows-arm-conan-center-index': true,
    'linux-x64-rhws6-conan-center-index': true,
    'linux-x64-rhel7-conan-center-index': true,
    'linux-arm-conan-center-index': true,
    'mac-x64-conan-center-index': true,
    'mac-arm-conan-center-index': true,
    'sparcsolaris-conan-center-index': true,
    'windows-conan-center-index': true,
]
def skipBuilding = false
// Don't upload things if the job name has 'test' in it
// Converting matcher to boolean with asBoolean() or find(): https://stackoverflow.com/a/35529715/11996393
def upload_ok = ! (env.JOB_NAME =~ 'test').find()

pipeline {
    parameters {
        choice(name: 'PLATFORM_FILTER',
               choices: ['all',
                         'aix-conan-center-index',
			 'windows-arm-conan-center-index',
                         'linux-x64-rhws6-conan-center-index',
                         'linux-x64-rhel7-conan-center-index',
                         'linux-arm-conan-center-index',
                         'mac-x64-conan-center-index',
                         'mac-arm-conan-center-index',
                         'sparcsolaris-conan-center-index',
                         'windows-conan-center-index'],
               description: 'Run on specific platform')
        booleanParam defaultValue: false, description: 'Completely clean the workspace before building, including the Conan cache', name: 'CLEAN_WORKSPACE'
        string(name: 'PYTEST_OPTIONS', defaultValue: '',
            description: 'Additional parameters for pytest, for instance, work on just swig with -k swig. See: https://docs.pytest.org/en/7.1.x/how-to/usage.html')
        booleanParam name: 'UPLOAD_ALL_RECIPES', defaultValue: false,
            description: 'Upload all recipes, instead of only recipes that changed since the last merge'
        booleanParam name: 'FORCE_TOOL_BUILD', defaultValue: false,
            description: 'Force build of all tools. By default, Conan will download the tool and test it if it\'s already built'
        booleanParam name: 'FORCE_TOOL_BUILD_WITH_REQUIREMENTS', defaultValue: false,
            description: 'Force build of all tools, and their requirements. By default, Conan will download the tool and test it if it\'s already built'
        booleanParam name: 'MERGE_UPSTREAM', defaultValue: false,
            description: 'If building develop branch, merge changes from upstream, i.e., conan-io/conan-center-index'
        booleanParam name: 'MERGE_STAGING_TO_PRODUCTION', defaultValue: false,
            description: 'If building master branch, merge changes from the develop branch'
    }
    options{
        buildDiscarder logRotator(artifactDaysToKeepStr: '4', artifactNumToKeepStr: '10', daysToKeepStr: '7', numToKeepStr: '10')
            disableConcurrentBuilds()
        timeout(time: 2, unit: "HOURS")
    }
    agent {
        node {
            label 'noarch-conan-center-index'
            customWorkspace "workspace/${JOB_NAME.replaceAll('/','_')}_noarch/"
        }
    }
    triggers {
        // From the doc: H(0-59) H(0-2) means some time between 12:00 AM and 2:59 AM.
        // This gives us automatic spreading out of jobs, so they don't cause load spikes.
        // See Syntax: https://www.jenkins.io/doc/book/pipeline/syntax/#cron-syntax
        // Note: Due to the when statement, MERGE_UPSTREAM only works on the develop branch, so
        // it doesn't have to be conditionalized here.
        // Randomly between 12:00AM and 2:59, run the job. On Sunday through Friday (0-5), just run the
        // job. On Saturday (6), use the MERGE_UPSTREAM=true parameter, which merges upstream if the
        // branch is develop
        parameterizedCron('''
            H(0-59) H(0-2) * * 0-5
            H(0-59) H(0-2) * * 6 % MERGE_UPSTREAM=true
        ''')
    }
    environment {
        CONAN_USER_HOME = "${WORKSPACE}"
        CONAN_NON_INTERACTIVE = '1'
        CONAN_PRINT_RUN_COMMANDS = '1'
        // Disable FileTracker on Windows, which can give FTK1011 on long path names
        TRACKFILEACCESS = 'false'
        // Disable node reuse, which gives intermittent build errors on Windows
        MSBUILDDISABLENODEREUSE = '1'
        // AIX workaround. Avoids an issue caused by the jenkins java process which sets
        // LIBPATH and causes errors downstream
        LIBPATH = "randomval"
        DL_CONAN_CENTER_INDEX = 'all'
        TOX_TESTENV_PASSENV = 'CONAN_USER_HOME CONAN_NON_INTERACTIVE CONAN_PRINT_RUN_COMMANDS CONAN_LOGIN_USERNAME CONAN_PASSWORD TRACKFILEACCESS MSBUILDDISABLENODEREUSE'
        // Create a personal access token on the devauto account on Octocat with repo and read:org access, and use it to
        // create a secret text credential with the name github-cli-devauto-octocat-access-token
        // See: https://cli.github.com/manual/gh_auth_login
        GH_ENTERPRISE_TOKEN = credentials('github-cli-devauto-octocat-access-token')
        // When using the token above 'gh help environment' says to also set GH_HOST
        // https://cli.github.com/manual/gh_help_environment
        GH_HOST = 'octocat.dlogics.com'
    }
    stages {
        stage('Clean/reset Git checkout for release') {
            when {
                anyOf {
                    expression { params.CLEAN_WORKSPACE }
                }
            }
            steps {
                echo "Clean noarch"
                script {
                    // Ensure that the checkout is clean and any changes
                    // to .gitattributes and .gitignore have been taken
                    // into effect
                    //
                    // The extra -f causes Git to delete even embedded Git
                    // repositories, which can happen if the Conan cache
                    // is in ./.conan, and a recipe (like SWIG) checks out
                    // its code with Git.
                    //
                    // See: https://git-scm.com/docs/git-clean#Documentation/git-clean.txt--f
                    if (isUnix()) {
                        sh """
                        git rm -q -r .
                        git reset --hard HEAD
                        git clean -f -fdx
                        """
                    } else {
                        // On Windows, 'git clean' can't handle long paths in .conan,
                        // so remove that first.
                        bat """
                        if exist ${WORKSPACE}\\.conan\\ rmdir/s/q ${WORKSPACE}\\.conan
                            git rm -q -r .
                            git reset --hard HEAD
                            git clean -f -fdx
                            """
                    }
                }
            }
        }
        stage('Set-Up Environment') {
            steps {
                printPlatformNameInStep('noarch')
                echo "Set-Up Environment noarch"
                script {
                    if (isUnix()) {
                        sh './mkenv.py --verbose'
                        ENV_LOC['noarch'] = sh (
                            script: './mkenv.py --env-name',
                            returnStdout: true
                        ).trim()
                    } else {
                        // Using the mkenv.py script like this assumes the Python Launcher is
                        // installed on the Windows host.
                        // https://docs.python.org/3/using/windows.html#launcher
                        bat '.\\mkenv.py --verbose'
                        ENV_LOC['noarch'] = bat (
                            // The @ prevents Windows from echoing the command itself into the stdout,
                            // which would corrupt the value of the returned data.
                            script: '@.\\mkenv.py --env-name',
                            returnStdout: true
                        ).trim()
                    }
                }
            }
        }
        stage('Set up Conan') {
            steps {
                sh """. ${ENV_LOC['noarch']}/bin/activate
                  invoke conan.login"""
            }
        }
        stage('flake8') {
            steps {
                catchError(message: 'flake8 had errors', stageResult: 'FAILURE') {
                    script {
                        sh """. ${ENV_LOC['noarch']}/bin/activate
                                    rm -f flake8.log
                                    flake8 --format=pylint --output=flake8.log --tee"""
                    }
                }
            }
            post {
                always {
                    recordIssues(enabledForFailure: true,
                                 tool: flake8(pattern: 'flake8.log'),
                                 qualityGates: [[threshold: 1, type: 'TOTAL', unstable: false]])
                }
            }
        }
        stage('Pre-commit checks') {
            when {
                changeRequest()
            }
            steps {
                catchError(message: 'pre-commit had errors', stageResult: 'FAILURE') {
                    script {
                        if (isUnix()) {
                            sh  """
                                        . ${ENV_LOC['noarch']}/bin/activate
                                        invoke jenkins.pre-commit
                                        """
                        } else {
                            bat """
                                        CALL ${ENV_LOC['noarch']}\\Scripts\\activate
                                        invoke jenkins.pre-commit
                                        """
                        }
                    }
                }
            }
        }
        stage('Merge from upstream') {
            when {
                expression {
                    // Merge upstream on develop-prefixed branches if forced by parameter
                    // The parametrized Cron timer sets MERGE_UPSTREAM at appropriate times.
                    env.BRANCH_NAME =~ 'develop' && params.MERGE_UPSTREAM
                }
            }
            steps {
                script {
                    sh  """
                    . ${ENV_LOC['noarch']}/bin/activate
                    invoke merge-upstream
                    """
                    def merge_upstream_status = readFile(file: '.merge-upstream-status')
                    echo "merge-upstream status is ${merge_upstream_status}"
                    // If the status of the upstream merge is MERGED, then don't do anything
                    // else; Jenkins will notice the branch changed and re-run.
                    skipBuilding = merge_upstream_status == 'MERGED'
                }
            }
        }
        stage('Merge staging to production') {
            when {
                expression {
                    // Merge upstream on master-prefixed branches if forced by parameter
                    env.BRANCH_NAME =~ 'master' && params.MERGE_STAGING_TO_PRODUCTION
                }
            }
            steps {
                script {
                    sh  """
                    . ${ENV_LOC['noarch']}/bin/activate
                    invoke merge-staging-to-production
                    """
                    def merge_staging_to_production_status = readFile(file: '.merge-staging-to-production-status')
                    echo "merge-staging-to-production status is ${merge_staging_to_production_status}"
                    // If the status of the merge is MERGED, then don't do anything
                    // else; Jenkins will notice the branch changed and re-run.
                    skipBuilding = merge_staging_to_production_status == 'MERGED'
                }
            }
        }
        stage('Upload new or changed recipes') {
            when {
                allOf {
                    expression { !skipBuilding && upload_ok }
                    not { changeRequest() }
                }
            }
            steps {
                script {
                    def remote
                    if (env.BRANCH_NAME =~ 'master') {
                        remote = 'conan-center-dl'
                    } else {
                        remote = 'conan-center-dl-staging'
                    }
                    def range
                    if (params.UPLOAD_ALL_RECIPES) {
                        range = '--all'
                    } else {
                        // make sure conan-io is available and up-to-date
                        sh "git remote | grep conan-io || git remote add conan-io https://github.com/conan-io/conan-center-index.git"
                        sh "git fetch conan-io"
                        // assuming this is due to a merge, upload recipes
                        // modified since just before the last merge. This is an
                        // incremental update to recipes, and will be much faster
                        // than uploading all 1100+ recipes.
                        range = "--since-before-last-merge --since-merge-from-branch=conan-io/master"
                    }
                    sh ". ${ENV_LOC['noarch']}/bin/activate; invoke upload-recipes --remote ${remote} ${range}"
                }
            }
        }
        stage('Per-platform') {
            matrix {
                agent {
                    node {
                        label "${NODE}"
                        customWorkspace "workspace/${JOB_NAME.replaceAll('/','_')}/"
                    }
                }
                when { anyOf {
                    expression { params.PLATFORM_FILTER == 'all' && !skipBuilding }
                    expression { params.PLATFORM_FILTER == env.NODE && !skipBuilding }
                } }
                axes {
                    axis {
                        name 'NODE'
                        values 'aix-conan-center-index',
                            'windows-arm-conan-center-index',
                            'linux-x64-rhws6-conan-center-index',
                            'linux-x64-rhel7-conan-center-index',
                            'linux-arm-conan-center-index',
                            'mac-x64-conan-center-index',
                            'mac-arm-conan-center-index',
                            'sparcsolaris-conan-center-index',
                            'windows-conan-center-index'
                    }
                }
                environment {
                    CONAN_USER_HOME = "${WORKSPACE}"
                    DL_CONAN_CENTER_INDEX = productionOrStaging()
                }
                stages {
                    stage('Clean/reset Git checkout for release') {
                        when {
                            anyOf {
                                expression { params.CLEAN_WORKSPACE }
                            }
                        }
                        steps {
                            echo "Clean ${NODE}"
                            script {
                                // Ensure that the checkout is clean and any changes
                                // to .gitattributes and .gitignore have been taken
                                // into effect
                                if (isUnix()) {
                                    sh """
                                        git rm -q -r .
                                        git reset --hard HEAD
                                        git clean -f -fdx
                                        """
                                } else {
                                    // On Windows, 'git clean' can't handle long paths in .conan,
                                    // so remove that first.
                                    bat """
                                        if exist ${WORKSPACE}\\.conan\\ rmdir/s/q ${WORKSPACE}\\.conan
                                        git rm -q -r .
                                        git reset --hard HEAD
                                        git clean -f -fdx
                                        """
                                }
                            }
                        }
                    }
                    stage('Set-Up Environment') {
                        steps {
                            printPlatformNameInStep(NODE)
                            echo "Set-Up Environment ${NODE}"
                            script {
                                if (isUnix()) {
                                    sh './mkenv.py --verbose'
                                    ENV_LOC[NODE] = sh (
                                        script: './mkenv.py --env-name',
                                        returnStdout: true
                                    ).trim()
                                } else {
                                    // Using the mkenv.py script like this assumes the Python Launcher is
                                    // installed on the Windows host.
                                    // https://docs.python.org/3/using/windows.html#launcher
                                    bat '.\\mkenv.py --verbose'
                                    ENV_LOC[NODE] = bat (
                                        // The @ prevents Windows from echoing the command itself into the stdout,
                                        // which would corrupt the value of the returned data.
                                        script: '@.\\mkenv.py --env-name',
                                        returnStdout: true
                                    ).trim()
                                }
                            }
                        }
                    }
                    stage('Print environment') {
                        steps {
                            script {
                                if (isUnix()) {
                                    sh "env"
                                } else {
                                    bat "set"
                                }
                            }
                        }
                    }
                    stage('Set up Conan') {
                        steps {
                            script {
                                if (isUnix()) {
                                    sh """. ${ENV_LOC[NODE]}/bin/activate
                                        invoke conan.login"""
                                } else {
                                    bat """CALL ${ENV_LOC[NODE]}\\Scripts\\activate
                                        invoke conan.login"""
                                }
                            }
                        }
                    }
                    stage('build tools') {
                        when {
                            expression { BUILD_TOOLS[NODE] }
                        }
                        steps {
                            script {
                                def upload = ""
                                if (env.CHANGE_ID == null && upload_ok) {  // i.e. not a pull request, and uploads are permitted
                                    if (env.BRANCH_NAME =~ 'master') {
                                        upload = '--upload-to conan-center-dl'
                                    } else {
                                        upload = '--upload-to conan-center-dl-staging'
                                    }
                                }
                                def short_node = NODE.replace('-conan-center-index', '')
                                def force_build
                                if (params.FORCE_TOOL_BUILD_WITH_REQUIREMENTS) {
                                    force_build = '--force-build with-requirements'
                                } else if (params.FORCE_TOOL_BUILD) {
                                    force_build = '--force-build'
                                } else {
                                    force_build = ''
                                }
                                def pytest_command = "pytest -k build_tool ${force_build} ${upload} --junitxml=build-tools.xml --html=${short_node}-build-tools.html ${params.PYTEST_OPTIONS}"
                                if (isUnix()) {
                                    catchError(message: 'pytest had errors', stageResult: 'FAILURE') {
                                        script {
                                            // on macOS, /usr/local/bin is not in the path by default, and the
                                            // Python binaries tox is looking for may be in there
                                            sh """. ${ENV_LOC[NODE]}/bin/activate
                                                (env PATH=\$PATH:/usr/local/bin ${pytest_command})"""
                                        }
                                    }
                                }
                                else {
                                    catchError(message: 'pytest had errors', stageResult: 'FAILURE') {
                                        script {
                                            bat """CALL ${ENV_LOC[NODE]}\\Scripts\\activate
                                                ${pytest_command}"""
                                        }
                                    }
                                }
                            }
                        }
                        post {
                            always {
                                catchError(message: 'testing had errors', stageResult: 'FAILURE') {
                                    xunit (
                                        reduceLog: false,
                                        tools: [
                                            JUnit(deleteOutputFiles: true,
                                                  failIfNotNew: true,
                                                  pattern: 'build-tools.xml',
                                                  skipNoTestFiles: true,
                                                  stopProcessingIfError: true)
                                        ])
                                    archiveArtifacts allowEmptyArchive: true, artifacts: '*-build-tools.html', followSymlinks: false
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        unsuccessful {
            script {
                if (env.CHANGE_ID == null) {  // i.e. not a pull request; those notify in GitHub
                    slackSend(channel: "#conan",
                              message: "Unsuccessful build: ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)",
                              color: "danger")
                }
            }
        }
        fixed {
            script {
                if (env.CHANGE_ID == null) {  // i.e. not a pull request; those notify in GitHub
                    slackSend(channel: "#conan",
                              message: "Build is now working: ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)",
                              color: "good")
                }
            }
        }
    }
}

void productionOrStaging() {
    if (env.CHANGE_ID == null) {
        if (env.BRANCH_NAME =~ 'master') {
            return 'production'
        } else {
            return 'staging'
        }
    } else {
        if (env.CHANGE_BRANCH =~ 'master') {
            return 'production'
        } else {
            return 'staging'
        }
    }
}

void printPlatformNameInStep(String node) {
    script {
        stage("Building on ${node}") {
            echo "Building on node: ${node}"
        }
    }
}
