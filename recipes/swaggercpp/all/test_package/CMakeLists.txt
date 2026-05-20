cmake_minimum_required(VERSION 3.26)
project(test_package CXX)

find_package(swaggercpp CONFIG REQUIRED)

add_executable(swaggercpp_test_package src/example.cpp)
target_link_libraries(swaggercpp_test_package PRIVATE swaggercpp::swaggercpp)
target_compile_features(swaggercpp_test_package PRIVATE cxx_std_23)
