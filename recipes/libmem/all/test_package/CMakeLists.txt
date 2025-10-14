cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(libmem REQUIRED CONFIG)

add_executable(test_package_c test_package_c.c)
target_link_libraries(test_package_c libmem::libmem)
target_compile_features(test_package_c PRIVATE c_std_11)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE libmem::libmem)
target_compile_features(test_package PRIVATE cxx_std_17)
