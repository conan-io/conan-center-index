cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(chronicle CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE chronicle::core)
target_compile_features(test_package PRIVATE cxx_std_23)
