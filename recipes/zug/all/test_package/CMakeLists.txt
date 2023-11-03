cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(zug REQUIRED CONFIG)

add_executable(test_package example.cpp)
target_link_libraries(test_package zug::zug)
set_target_properties(test_package PROPERTIES CXX_STANDARD 14)
