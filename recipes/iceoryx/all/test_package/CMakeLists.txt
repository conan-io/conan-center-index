cmake_minimum_required(VERSION 3.15)
project(test_package)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD 14)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(iceoryx REQUIRED CONFIG)

add_executable(test_package main.cpp)
target_link_libraries(test_package  iceoryx_posh::iceoryx_posh
                            iceoryx_posh::iceoryx_posh_roudi
)
