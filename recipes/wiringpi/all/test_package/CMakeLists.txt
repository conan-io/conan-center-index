cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(wiringpi REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_link_libraries(test_package wiringpi::wiringpi)
