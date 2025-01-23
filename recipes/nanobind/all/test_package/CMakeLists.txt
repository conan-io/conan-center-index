cmake_minimum_required(VERSION 3.18)
project(test_package CXX)

find_package(Python 3.8 REQUIRED COMPONENTS Development.Module)

if(Python_NATIVE_EXECUTABLE)
    set(Python_EXECUTABLE ${Python_NATIVE_EXECUTABLE})
endif()

find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(test_package NB_STATIC test_package.cpp)
