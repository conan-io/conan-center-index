#!/bin/bash

if [ ! -d "./build" ]; then
    cmake --preset=dev &> /dev/null
fi

find ./build -name "*.gcda" -type f -delete &> /dev/null
find ./build -name "*.gcno" -type f -delete &> /dev/null
rm -f ./build/test/samarium_tests

echo "Compiling..."
./scripts/build.sh
echo "Done"
~/bin/tryrun ./build/test/samarium_tests
