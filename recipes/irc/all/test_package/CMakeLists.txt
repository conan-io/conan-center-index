cmake_minimum_required(VERSION 3.16)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(irc REQUIRED CONFIG)

add_executable(test_package main.cpp)

target_link_libraries(test_package PRIVATE irc::irc)
