cmake_minimum_required(VERSION 3.4)
project(test_package CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_output_dirs_setup()
conan_set_rpath()
conan_set_std()
conan_set_fpic()
conan_check_compiler()
conan_set_libcxx()
conan_set_vs_runtime()

find_package(pybind11 REQUIRED CONFIG)

pybind11_add_module(test_package MODULE test_package.cpp)
set_property(TARGET test_package PROPERTY CXX_STANDARD 11)
