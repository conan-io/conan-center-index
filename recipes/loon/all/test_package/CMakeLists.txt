cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(loon REQUIRED)

add_executable(test_package src/test_package.cpp)
target_link_libraries(test_package PRIVATE loon::loon)
