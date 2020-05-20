cmake_minimum_required(VERSION 2.8.12)

PROJECT(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
set_property(TARGET test_package PROPERTY CXX_STANDARD 17)
