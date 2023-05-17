cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(trompeloeil REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE trompeloeil::trompeloeil)
target_compile_features(test_package PRIVATE cxx_std_14)
