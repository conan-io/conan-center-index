cmake_minimum_required(VERSION 3.0)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include("CMakeListsOriginal.txt")
