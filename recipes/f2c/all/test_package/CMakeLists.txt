cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES Fortran)

get_filename_component(Fortran_COMPILER_NAME ${CMAKE_Fortran_COMPILER} NAME)
if(NOT Fortran_COMPILER_NAME STREQUAL "fc")
    message(FATAL_ERROR "Failed to use fc as the Fortran compiler")
endif()

add_executable(${PROJECT_NAME} test_package.f)
