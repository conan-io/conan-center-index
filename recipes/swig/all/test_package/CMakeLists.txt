cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(SWIG REQUIRED)
include(UseSWIG)

find_package(Python REQUIRED COMPONENTS Interpreter Development)

swig_add_library(${PROJECT_NAME}
    LANGUAGE python
    SOURCES test.i test_package.c
)
target_link_libraries(${PROJECT_NAME} PRIVATE Python::Python)
