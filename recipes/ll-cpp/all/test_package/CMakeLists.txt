cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ll-cpp CONFIG REQUIRED)

add_executable(ll-cpp-test test_package.cpp)
target_link_libraries(ll-cpp-test PRIVATE llcpp::llcpp)
set_property(TARGET ll-cpp-test PROPERTY CXX_STANDARD 17)
