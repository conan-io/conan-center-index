cmake_minimum_required(VERSION 3.1)
PROJECT(test_package CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP(TARGETS)

find_package(ApprovalTests REQUIRED CONFIG)

ADD_EXECUTABLE(test_package test_package.cpp)
target_link_libraries(test_package ApprovalTests::ApprovalTests)
