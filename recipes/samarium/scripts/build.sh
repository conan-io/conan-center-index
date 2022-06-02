#!/bin/bash

mold -run cmake --build --preset=default &> ./build/output
sed -i 's#home##g' ./build/output
sed -i 's#jb##g' ./build/output
sed -i 's#src##g' ./build/output
sed -i 's#samarium##g' ./build/output
sed -i 's#CMakeFiles##g' ./build/output
sed -i 's#.dir##g' ./build/output
sed -i 's#//##g' ./build/output
gawk -i inplace '!/FAILED/' ./build/output
gawk -i inplace '!/terminated/' ./build/output
gawk -i inplace '!/Makefile/' ./build/output
gawk -i inplace '!/test_tests/' ./build/output
gawk -i inplace '!/subcommand/' ./build/output
gawk -i inplace '!/HAS_FCHOWN/' ./build/output
gawk -i inplace '!/CXX/' ./build/output
cat ./build/output
exit $?
