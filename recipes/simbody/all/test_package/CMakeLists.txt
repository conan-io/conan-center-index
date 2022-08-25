cmake_minimum_required(VERSION 3.10.2)
project(test_package VERSION 1.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(simbody3 REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package simbody3::simbody3)