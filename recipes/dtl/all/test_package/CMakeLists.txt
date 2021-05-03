cmake_minimum_required(VERSION 3.18)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)
