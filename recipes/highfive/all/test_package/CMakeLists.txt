cmake_minimum_required(VERSION 3.1)

project(test_package LANGUAGES C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(HighFive 2.3 REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package HighFive::HighFive)
