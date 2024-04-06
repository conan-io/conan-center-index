cmake_minimum_required(VERSION 3.15)
project(TestPackage CXX)

find_package(mathter REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE mathter::mathter)
target_compile_features(test_package PRIVATE cxx_std_17)
