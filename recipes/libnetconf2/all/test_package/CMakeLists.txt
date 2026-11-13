cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(LibNETCONF2 CONFIG REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE libnetconf2::libnetconf2)
