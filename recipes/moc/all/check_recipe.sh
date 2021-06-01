#/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}" )"
scriptDir=$(pwd)

export RECIPE_FOLDER=${RECIPE_FOLDER:-recipe_check}
cd "$scriptDir"

PROGRAM=$0

Usage() {
    echo "USAGE: $PROGRAM [build|clean|add_version}"
}

checkExeExists() {
    local missing=""
    while [ $# -gt 0 ] ; do
        if ! type 2>/dev/null >/dev/null -p "$1" ; then
            missing="$missing $1"
        fi
        shift
    done
    [ -z $missing ] || fatal "Please install and add the following to your PATH:$missing"
}

fatal() {
    exitcode=$1
    shift
    echo >&2 "$*"
    exit $exitcode
}

clean() {
    [ ! -z "$RECIPE_FOLDER" ] && rm -rf "$RECIPE_FOLDER"
}

build() {
    clean;
    mkdir -p "${RECIPE_FOLDER}"
    cd "${RECIPE_FOLDER}"
    checkExeExists conan
    conan install  .. --install-folder=cmake-build-debug # [--profile XXXX]
    conan source ..  --source-folder=raw_src
    conan build ..  --install-folder=cmake-build-debug --source-folder=raw_src
    conan package .. --build-folder=cmake-build-debug --package-folder=package-folder  --source-folder=raw_src
}

calcsha() {
    checkExeExists shasum awk

    local file=$1
    [ ! -z "$file" ] || fatal "USAGE $PROGRAM $0 {file}"
    sha=$(shasum -a 256 "$file"|awk '{print $1}')
    echo $sha
}

    
add_version() {
    if [ $# = 0 ] ; then
        echo >&2 "Missing verion. $PROGRAM $0 '{github-version-tag}'"
        return 1
    fi
    mkdir -p "${RECIPE_FOLDER}"
    cd "${RECIPE_FOLDER}"

    checkExeExists curl shasum awk

    tag=$1
    if grep >/dev/null 2>&1 "\"$tag\":" ../conandata.yml; then
        echo >&2 "found '$tag' in conandata already. Nothing to be done"
        return 1
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
            Usage;
            return 0
            ;;
    esac
}

main "$@"
