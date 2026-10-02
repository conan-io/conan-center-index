cmake_minimum_required(VERSION 3.15)
project(nwau_c_abi_test_package C)

find_package(nwau-c-abi REQUIRED CONFIG)

add_executable(test_package src/test_package.c)
target_link_libraries(test_package PRIVATE nwau-c-abi::nwau-c-abi)
