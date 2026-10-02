cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(perf-cpp REQUIRED CONFIG)

add_executable(test_package src/test_package.cpp)
target_link_libraries(test_package PRIVATE perf-cpp::perf-cpp)
target_compile_features(test_package PRIVATE cxx_std_17)
