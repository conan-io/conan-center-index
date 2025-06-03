cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(sparrow REQUIRED CONFIG)

add_executable(standalone main.cpp)

target_link_libraries(standalone PRIVATE sparrow::sparrow)
target_compile_features(standalone PRIVATE cxx_std_20)
