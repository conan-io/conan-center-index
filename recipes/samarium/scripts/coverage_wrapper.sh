#!/bin/bash

rm -rf ./build
cmake --preset=coverage >/dev/null
cmake --build --preset=default >/dev/null
./scripts/coverage.sh
grep -v "functionToCover" ./coverage.xml > tmpfile && mv tmpfile coverage.xml
