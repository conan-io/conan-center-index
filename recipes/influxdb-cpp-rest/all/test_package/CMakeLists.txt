cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(influxdb-cpp-rest REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE influxdb-cpp-rest::influxdb-cpp-rest)

add_executable(test_c_rest test_c_rest.cpp)
target_link_libraries(test_c_rest PRIVATE influxdb-cpp-rest::influx-c-rest)
