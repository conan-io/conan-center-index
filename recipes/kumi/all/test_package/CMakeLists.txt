cmake_minimum_required(VERSION 3.22)
project(test_package LANGUAGES CXX)

find_package(kumi REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE kumi::kumi)
target_compile_features(test_package PRIVATE cxx_std_20)
