project(cmake_wrapper)
cmake_minimum_required(VERSION 3.1)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_subdirectory("source_subfolder")
