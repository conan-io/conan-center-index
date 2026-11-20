cmake_minimum_required(VERSION 3.20)
project(test_package CXX)

find_package(praxo-cpp CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE praxo::praxo_cpp)

enable_testing()
add_test(NAME test_package COMMAND test_package)
