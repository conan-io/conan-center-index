#!/usr/bin/env bash

upstream_url=https://github.com/conan-io/conan-center-index.git

if ! git config remote.upstream.url > /dev/null; then
    git remote add upstream https://github.com/conan-io/conan-center-index.git
fi

git fetch upstream

