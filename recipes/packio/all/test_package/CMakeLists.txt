cmake_minimum_required(VERSION 3.15)
project(TestPackage CXX)

find_package(packio REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package PRIVATE packio::packio)
