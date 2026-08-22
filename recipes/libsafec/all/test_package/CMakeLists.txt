cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(libsafec REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE libsafec::libsafec)
