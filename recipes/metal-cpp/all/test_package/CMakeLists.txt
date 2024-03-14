cmake_minimum_required(VERSION 3.12)
project(test_pacakge LANGUAGES CXX)

find_package(metal-cpp REQUIRED)

add_executable(test_package test_package.cpp)

if(TARGET metal-cpp::metal-cpp)
    target_link_libraries(test_package  PRIVATE  metal-cpp::metal-cpp)
else()
    target_link_libraries(test_package  PRIVATE  metal-cpp::metal-cpp-header-only)
endif()
