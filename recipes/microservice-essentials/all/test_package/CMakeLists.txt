cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(microservice-essentials REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package microservice-essentials::microservice-essentials)
