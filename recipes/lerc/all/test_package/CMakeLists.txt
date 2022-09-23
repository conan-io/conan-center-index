cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(lerc REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE lerc::lerc)
