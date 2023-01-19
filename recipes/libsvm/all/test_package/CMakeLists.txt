cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(libsvm CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE libsvm::libsvm)
