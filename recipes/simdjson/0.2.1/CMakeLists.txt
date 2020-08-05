cmake_minimum_required(VERSION 3.9)

project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_subdirectory(source_subfolder)

