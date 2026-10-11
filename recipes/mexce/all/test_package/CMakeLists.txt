cmake_minimum_required(VERSION 3.15)
project(mexce_test_package LANGUAGES CXX)

find_package(mexce CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE mexce::mexce)

if(TARGET mexce::protected)
    add_executable(test_protected test_protected.cpp)
    target_link_libraries(test_protected PRIVATE mexce::protected)
endif()
