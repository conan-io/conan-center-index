cmake_minimum_required(VERSION 3.15)
project(test_package C)

add_executable(test_package test_package.c)

if(NOT WIN32)
    target_link_libraries(test_package PRIVATE ${CMAKE_DL_LIBS})
endif()
