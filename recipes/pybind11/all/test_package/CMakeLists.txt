cmake_minimum_required(VERSION 2.8.11)
project(test_package CXX)

find_package(pybind11 REQUIRED)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_global_flags()

pybind11_add_module(test_package MODULE
    test_package.cpp
)
