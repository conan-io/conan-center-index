cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(nodejs-headers REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package nodejs-headers::nodejs-headers)
