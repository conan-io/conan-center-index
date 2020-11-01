cmake_minimum_required(VERSION 3.14)
project(conanllvm)

message(STATUS "Conan CMake Wrapper")
include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source")
