cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(aerospike-common REQUIRED CONFIG)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE aerospike-common::aerospike-common)