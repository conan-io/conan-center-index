cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(iceoryx REQUIRED CONFIG)

add_executable(test_package main.cpp)
target_link_libraries(test_package
    iceoryx_posh::iceoryx_posh
    iceoryx_posh::iceoryx_posh_roudi
)

if (iceoryx_VERSION LESS_EQUAL "2.0.6")
    target_compile_definitions(test_package PRIVATE OLD_SYNTAX)
endif()
