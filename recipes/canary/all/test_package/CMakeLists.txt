cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(canary REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PUBLIC canary::canary)
target_compile_features(test_package PRIVATE cxx_std_11)
