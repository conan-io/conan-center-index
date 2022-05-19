cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(md4c CONFIG REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package md4c::md4c)
