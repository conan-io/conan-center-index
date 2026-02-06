cmake_minimum_required(VERSION 3.15)
project(sintra_test_package LANGUAGES CXX)

find_package(sintra CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE sintra::sintra)
