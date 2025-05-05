cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(tsil REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE tsil::tsil)
