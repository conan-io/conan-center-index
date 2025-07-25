cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(librdtsc CONFIG REQUIRED)

add_executable(example test_package.c)
target_link_libraries(example librdtsc::librdtsc)

