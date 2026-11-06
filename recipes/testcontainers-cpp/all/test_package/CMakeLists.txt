cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

# The package promises this exact find_package name and target (the Conan
# reference stays testcontainers-cpp; see package_info in ../conanfile.py).
find_package(testcontainers REQUIRED CONFIG)

add_executable(test_package src/test_package.cpp)
target_link_libraries(test_package PRIVATE testcontainers::testcontainers)
