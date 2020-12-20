cmake_minimum_required(VERSION 3.10)
project(test_package CXX)

find_package(qpOASES REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package PRIVATE qpOASES::qpOASES)
