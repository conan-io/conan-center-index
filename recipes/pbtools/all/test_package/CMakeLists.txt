cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(pbtools REQUIRED CONFIG)

add_executable(test_package test_package.c hello_world.c)
target_link_libraries(test_package pbtools::pbtools)
