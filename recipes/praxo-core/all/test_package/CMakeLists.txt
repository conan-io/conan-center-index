cmake_minimum_required(VERSION 3.20)
project(test_package C)

find_package(praxo-core CONFIG REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE praxo::praxo_core)

enable_testing()
add_test(NAME test_package COMMAND test_package)
