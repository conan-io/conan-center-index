cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(unilink REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package unilink::unilink)

target_compile_features(test_package PRIVATE cxx_std_17)
