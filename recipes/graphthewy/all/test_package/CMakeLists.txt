cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(graphthewy REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE graphthewy::graphthewy)
set_property(TARGET test_package PROPERTY CXX_STANDARD 17)
