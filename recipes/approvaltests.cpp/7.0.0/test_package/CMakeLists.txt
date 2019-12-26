cmake_minimum_required(VERSION 2.8)
PROJECT(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
