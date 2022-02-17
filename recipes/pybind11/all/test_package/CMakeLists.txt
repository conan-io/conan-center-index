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

find_package(pybind11 REQUIRED)

pybind11_add_module(test_package MODULE test_package.cpp)
set_property(TARGET test_package PROPERTY CXX_STANDARD 11)

enable_testing()

add_test(run_example
  ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test.py ${CMAKE_CURRENT_BINARY_DIR}/lib)
