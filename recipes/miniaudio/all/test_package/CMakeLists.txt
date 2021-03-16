cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(miniaudio REQUIRED)

add_executable(test_package example.c)
target_link_libraries(test_package miniaudio::miniaudio)
