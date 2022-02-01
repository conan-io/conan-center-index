cmake_minimum_required(VERSION 3.1)

project(test_package LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(HighFive 2.3 REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package HighFive::HighFive)
