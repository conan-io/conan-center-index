cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C CXX)

find_package(tiny-aes-c REQUIRED CONFIG)

add_executable(test_package_c test_package.c)
add_executable(test_package_cpp test_package.cpp)

target_link_libraries(test_package_c PRIVATE tiny-aes-c::tiny-aes-c)
target_link_libraries(test_package_cpp PRIVATE tiny-aes-c::tiny-aes-c)
