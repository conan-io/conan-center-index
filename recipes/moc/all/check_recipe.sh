#/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}" )"
scriptDir=$(pwd)

export RECIPE_FOLDER=${RECIPE_FOLDER:-recipe_check}
cd "$scriptDir"
export PACKAGE_FOLDER=${PACKAGE_FOLDER:-package-folder}
export CMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE:-Debug}
export CMAKE_BUILD_DIR=${CMAKE_BUILD_DIR:-cmake-build-debug}

PROGRAM=$0

Usage() {
    echo "
USAGE: $PROGRAM [build|clean|add_version|calcsha|test-package}
    build - builds the app
    clean - removes the build folders
    add_version {verision-tag} - adds a new version to the conandata.yml file
    test-package  {verision-tag} - adds a new version to the conandata.yml file
    calcsha {file} - calculate the sha256 of the file
    help - show this usage.
"
}

checkExeExists() {
    local missing=""
    while [ $# -gt 0 ] ; do
        if ! type 2>/dev/null >/dev/null -p "$1" ; then
            missing="$missing $1"
        fi
        shift
    done
    [ -z $missing ] || fatal 1 "
Please install and add the following to your PATH:$missing
"
}

fatal() {
    exitcode=$1
    shift
    echo >&2 "$*"
    Usage
    exit $exitcode
}

clean() {
    cd "$scriptDir"
    [ ! -z "$RECIPE_FOLDER" ] && rm -rf "$RECIPE_FOLDER"
    [ ! -z "$CMAKE_BUILD_DIR" ] && rm -rf "$CMAKE_BUILD_DIR"
    rm -rf "src"
}

build() {
    clean;
    mkdir -p "${RECIPE_FOLDER}"
    cd "${RECIPE_FOLDER}"
    checkExeExists conan
    folders=" --install-folder=${CMAKE_BUILD_DIR} "
    conan install  .. $folders
    folders=" $folders  --source-folder=raw_src  "
    conan source .. $folders
    folders=" $folders  --build-folder=${CMAKE_BUILD_DIR} "
    conan build ..  $folders
    folders=" $folders --package-folder=${PACKAGE_FOLDER} "
    conan package .. $folders
}

calcsha() {
    checkExeExists shasum awk

    local file=$1
    [ ! -z "$file" ] || fatal 2 "
Missing file to calculate sha 
"
    sha=$(shasum -a 256 "$file"|awk '{print $1}')
    echo $sha
}

    
add_version() {
    if [ $# = 0 ] ; then
        fatal 3 "
Missing verion. $PROGRAM $0 '{github-version-tag}'
e.g: $PROGRM $0 0.9.2
"
        return 3
    fi
    mkdir -p "${RECIPE_FOLDER}"
    cd "${RECIPE_FOLDER}"

    checkExeExists curl shasum awk

    tag=$1
    if grep >/dev/null 2>&1 "\"$tag\":" ../conandata.yml; then
        fatal 4 "
found '$tag' in conandata already. Nothing to be done
"
        return 4
    fi
    file=${tag}.tar.gz
    rm -f "$file"
    tar_url="https://github.com/zuut/moc/archive/refs/tags/${file}"
    curl -L -O "$tar_url"
    sha=$(calcsha "$file")
    cat >> ../conandata.yml <<EOF
  "$tag":
    # to calculate sha, shasum -a 256 {file}
    sha256: $sha
    url: "$tar_url"
EOF
    return 0
}

installConanPackage() {
    if [ $# = 0 ] ; then
        fatal 5 "
Missing verion. $PROGRAM $0 '{github-version-tag}'
e.g: $PROGRM $0 0.9.2
"
        return 5
    fi
    checkExeExists conan
    conan create . moc/$1@
}

main() {
    local command=${1:-build}
    shift
    case $command in
        build)
            build "$@"
            return $?
        ;;
        clean)
            clean "$@"
            return $?
        ;;
        add_version)
            add_version "$@"
            return $?
        ;;
        calcsha)
            calcsha "$@"
            return $?
        ;;
        test-package)
            installConanPackage "$@"
            return $?
        ;;
        -h)
            Usage;
            return 0
            ;;
        --help)
            Usage;
            return 0
            ;;
        help)
            Usage;
            return 0
            ;;
        *)
            echo >&2 "Unknown command $PROGRAM $command"
            Usage;
            return 0
            ;;
    esac
}

main "$@"
