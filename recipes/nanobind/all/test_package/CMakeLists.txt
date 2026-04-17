cmake_minimum_required(VERSION 3.20)
project(test_package CXX)
enable_testing()

set(Python_FIND_UNVERSIONED_NAMES FIRST)

find_package(Python REQUIRED COMPONENTS Development OPTIONAL_COMPONENTS Interpreter)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(conan_test_package NB_STATIC test_package.cpp)

if (Python_Interpreter_FOUND)
    add_test(NAME import_module
             COMMAND ${Python_EXECUTABLE} ${PROJECT_SOURCE_DIR}/test_package.py)
    set_tests_properties(import_module PROPERTIES
                         ENVIRONMENT "PYTHONPATH=$<TARGET_FILE_DIR:conan_test_package>")
endif()