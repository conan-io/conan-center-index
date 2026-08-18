cmake_minimum_required(VERSION 3.20)
project(test_package CXX)

find_package(sel-lang REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE sel-lang::sel-lang)
