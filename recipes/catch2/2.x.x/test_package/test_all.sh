#!/usr/bin/env bash
# Run with the package reference as an argument
set -ex
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
conan test $DIR $1 --build=catch2
conan test $DIR $1 --build=catch2 -o catch2:with_main=True -o catch2:with_benchmark=True 
conan test $DIR $1 --build=catch2 -o catch2:with_prefix=True 
conan test $DIR $1 --build=catch2 -o catch2:with_main=True -o catch2:with_prefix=True 
