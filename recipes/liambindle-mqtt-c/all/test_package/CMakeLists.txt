cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(liambindle-mqtt-c CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package liambindle-mqtt-c::liambindle-mqtt-c)
target_include_directories(test_package PRIVATE ${MBEDTLS_INCLUDE_DIRS})
