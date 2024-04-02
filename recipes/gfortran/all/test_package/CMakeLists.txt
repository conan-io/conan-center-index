cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES Fortran)

message("CMAKE_Fortran_COMPILER: ${CMAKE_Fortran_COMPILER}")

add_executable(${PROJECT_NAME} test_package.f90)
