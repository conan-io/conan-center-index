cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_program(CCCC cccc)

if(NOT CCCC)
    message(FATAL_ERROR "cccc not found")
endif()
