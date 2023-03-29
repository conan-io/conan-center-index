cmake_minimum_required(VERSION 3.24)
project(test_package LANGUAGES CXX)

find_package(OnnxRuntime REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE OnnxRuntime::OnnxRuntime)
target_compile_features(test_package PRIVATE cxx_std_17)
