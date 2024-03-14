cmake_minimum_required(VERSION 3.12)
project(test_pacakge LANGUAGES CXX)

find_package(metal-cpp REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package  PRIVATE  metal-cpp::metal-cpp)
