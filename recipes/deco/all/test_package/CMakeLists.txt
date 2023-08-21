cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(deco CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package deco::deco)
set_target_properties(test_package PROPERTIES CXX_STANDARD 17)
