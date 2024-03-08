cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(fuzztest REQUIRED CONFIG)

include(GoogleTest) # For gtest_discover_tests, built into CMake

add_executable(test_package test_package.cpp)

link_fuzztest(test_package)
gtest_discover_tests(test_package)
