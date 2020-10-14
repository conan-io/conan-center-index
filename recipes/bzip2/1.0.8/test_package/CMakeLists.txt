cmake_minimum_required(VERSION 3.1)
PROJECT(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(test_package test_package.c)
target_link_libraries(test_package ${CONAN_LIBS})
