cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

add_executable(test_package test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_17)

find_package(h5pp REQUIRED CONFIG)
target_link_libraries(test_package PRIVATE h5pp::h5pp)
