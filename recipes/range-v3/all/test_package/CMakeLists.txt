cmake_minimum_required(VERSION 3.5)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

find_package(range-v3)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} range-v3::range-v3)
set_property(TARGET test_package PROPERTY CXX_STANDARD 14)
