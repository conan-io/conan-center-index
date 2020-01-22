cmake_minimum_required(VERSION 2.8)
PROJECT(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(test_package test_catch.cpp)
#ADD_EXECUTABLE(test_package test_gtest.cpp)
#ADD_EXECUTABLE(test_package test_doctest.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
