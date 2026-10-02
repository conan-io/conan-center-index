cmake_minimum_required(VERSION 3.16)
project(test_package CXX)

find_package(mock-services CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package mock-services::mock-services)

enable_testing()
add_test(NAME test_package COMMAND test_package)
