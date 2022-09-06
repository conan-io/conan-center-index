cmake_minimum_required(VERSION 3.16)
project(test_package CXX)

find_package(Microsoft.GSL REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package Microsoft.GSL::GSL)
set_property(TARGET test_package PROPERTY CXX_STANDARD 14)
