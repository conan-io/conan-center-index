cmake_minimum_required(VERSION 3.4)
project(test_package CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(pybind11 REQUIRED)

pybind11_add_module(test_package MODULE
    test_package.cpp
)

enable_testing()

add_test(run_example
  ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test.py ${CMAKE_CURRENT_BINARY_DIR}/lib)
