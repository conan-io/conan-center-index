cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(libmem REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE libmem::libmem)
target_compile_features(test_package PRIVATE cxx_std_17)
target_compile_definitions(test_package PRIVATE _GNU_SOURCE=1)
