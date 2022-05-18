cmake_minimum_required(VERSION 3.1)
project(conan_wrapper CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(KEEP_RPATHS)

add_subdirectory("source_subfolder")
