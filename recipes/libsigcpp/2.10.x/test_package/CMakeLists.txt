PROJECT(test_package CXX)
cmake_minimum_required(VERSION 3.2)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})