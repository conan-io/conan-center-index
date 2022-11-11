cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Tracy REQUIRED CONFIG)

add_executable(test_package example.cpp)
target_link_libraries(test_package PRIVATE Tracy::TracyClient)
