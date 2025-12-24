cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(syscalls-cpp REQUIRED CONFIG)

add_executable(test_package main.cpp)

target_link_libraries(test_package PRIVATE sapdragon::syscalls-cpp)