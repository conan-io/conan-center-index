cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(SuiteSparse REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package PRIVATE SuiteSparse::SuiteSparse)