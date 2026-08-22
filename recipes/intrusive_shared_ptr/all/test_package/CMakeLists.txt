cmake_minimum_required(VERSION 3.15)
project(TestPackage CXX)

find_package(isptr CONFIG REQUIRED)

add_executable(test_package src/test.cpp)
target_link_libraries(test_package isptr::isptr)
target_compile_features(test_package PRIVATE cxx_std_17)

