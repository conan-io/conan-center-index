cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include("${CMAKE_BINARY_DIR}/conanbuild.info.cmake")
conan_basic_setup(TARGETS)

find_package(qpOASES REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package PRIVATE qpOASES::qpOASES)
