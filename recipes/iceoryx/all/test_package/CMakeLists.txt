cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)


find_package(iceoryx REQUIRED CONFIG)

add_executable(test_package main.cpp)
target_link_libraries(test_package
    iceoryx_posh::iceoryx_posh
    iceoryx_posh::iceoryx_posh_roudi
)
