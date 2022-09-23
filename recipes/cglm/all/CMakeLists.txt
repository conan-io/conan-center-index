cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory("source_subfolder")
