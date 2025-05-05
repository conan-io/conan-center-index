cmake_minimum_required(VERSION 3.12)

project(test_package CXX)
set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(SplunkOpenTelemetry CONFIG REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package SplunkOpenTelemetry::SplunkOpenTelemetry)
