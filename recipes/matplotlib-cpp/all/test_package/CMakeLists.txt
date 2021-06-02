cmake_minimum_required(VERSION 3.10)
project(test_package)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(matplotlib-cpp REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE matplotlib-cpp::matplotlib-cpp Python3::Python)
