cmake_minimum_required(VERSION 3.15)
set(CMAKE_VERBOSE_MAKEFILE ON)
project(test_package)

find_package(quickcpplib REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package quickcpplib::hl)

if ("${CMAKE_CXX_STANDARD}" STREQUAL "")
    if (TARGET span-lite::span-lite)
        target_compile_features(test_package PRIVATE cxx_std_17)
    endif ()
endif ()
