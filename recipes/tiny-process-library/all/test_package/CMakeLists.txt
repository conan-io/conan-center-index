cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(tiny-process-library CONFIG REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package PRIVATE tiny-process-library::tiny-process-library)