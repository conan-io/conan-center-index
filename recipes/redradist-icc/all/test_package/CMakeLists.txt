cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)

find_package(icc REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE icc::icc)
