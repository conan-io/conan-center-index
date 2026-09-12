cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES CXX)

find_package(nxpp CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE nxpp::nxpp)
