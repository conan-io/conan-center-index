cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(sdsl-lite CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package sdsl-lite::sdsl-lite)
set_property(TARGET test_package PROPERTY CXX_STANDARD 11)
