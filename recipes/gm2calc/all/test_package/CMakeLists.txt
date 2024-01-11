cmake_minimum_required(VERSION 3.15)
project(PackageTest C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(GM2Calc REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE GM2Calc::GM2Calc)
