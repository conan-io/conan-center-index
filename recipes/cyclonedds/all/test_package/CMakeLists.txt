cmake_minimum_required(VERSION 3.15)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(cyclonedds REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package CycloneDDS::ddsc
)
