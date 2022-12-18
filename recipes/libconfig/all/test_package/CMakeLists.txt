cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C CXX)

set(CMAKE_VERBOSE_MAKEFILE ON)

find_package(libconfig REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} libconfig::libconfig)

add_executable(${PROJECT_NAME}++ test_package.cpp)
target_link_libraries(${PROJECT_NAME}++ libconfig::libconfig++)
