cmake_minimum_required(VERSION 3.10)
project(test_package C)

find_package(libnetconf2 REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package libnetconf2::libnetconf2)
