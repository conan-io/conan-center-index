cmake_minimum_required(VERSION 3.4)
project(test_package CXX)


find_package(pybind11 REQUIRED)

pybind11_add_module(test_package MODULE test_package.cpp)
target_link_libraries(test_package PRIVATE pybind11::pybind11)
set_property(TARGET test_package PROPERTY CXX_STANDARD 11)

enable_testing()

add_test(run_example
  ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test.py ${CMAKE_CURRENT_BINARY_DIR}/lib)
