project(test_diplib LANGUAGES CXX)
cmake_minimum_required(VERSION 3.20)

find_package(DIPlib REQUIRED)
add_executable(test_package main.cpp)
target_link_libraries(test_package DIPlib::DIP)
