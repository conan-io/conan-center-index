cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

add_executable(test_package test_package.cpp)

find_package(ydcpp-tcpcat CONFIG REQUIRED)
target_link_libraries(test_package ydcpp-tcpcat)
target_compile_features(test_package PRIVATE cxx_std_17)
