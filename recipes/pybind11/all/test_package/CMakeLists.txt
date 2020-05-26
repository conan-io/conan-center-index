cmake_minimum_required(VERSION 2.8.11)
project(test_package CXX)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)

find_package(pybind11 REQUIRED)
include(pybind11Tools)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

pybind11_add_module(test_package MODULE
    test_package.cpp
)
