cmake_minimum_required(VERSION 3.10)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(sablib CONFIG REQUIRED)

add_executable(test_package src/main.cpp)
target_link_libraries(test_package PRIVATE sablib::sablib)
