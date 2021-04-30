cmake_minimum_required(VERSION 3.1)
project(PackageTest C Fortran)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(test_package test_package.f90)
target_link_libraries(test_package CONAN_PKG::collier)
