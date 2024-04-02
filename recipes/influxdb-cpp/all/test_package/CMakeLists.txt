cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(influxdb-cpp REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE influxdb-cpp::influxdb-cpp)
set_property(TARGET test_package PROPERTY CXX_STANDARD 11)
