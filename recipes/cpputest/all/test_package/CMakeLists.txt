cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(CppUTest REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE CppUTest)
target_compile_definitions(test_package PRIVATE $<$<BOOL:${WITH_EXTENSIONS}>:WITH_EXTENSIONS>)

