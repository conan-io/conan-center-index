cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
