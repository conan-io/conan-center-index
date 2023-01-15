cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(CGNS CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package CGNS::CGNS)
