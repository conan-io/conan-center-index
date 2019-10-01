cmake_minimum_required(VERSION 2.8.12)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(SWIG REQUIRED)
include(UseSWIG)

swig_add_library(${PROJECT_NAME}
    TYPE MODULE
    LANGUAGE python
    SOURCES
        test.i
        test_package.c
)
