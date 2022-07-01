cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(trompeloeil REQUIRED)

add_executable(test_package example.cpp)
target_link_libraries(test_package trompeloeil::trompeloeil)
set_property(TARGET test_package PROPERTY CXX_STANDARD 14)
