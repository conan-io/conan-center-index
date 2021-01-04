cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

message("Conan CMake Wrapper")
include("conanbuildinfo.cmake")
conan_basic_setup()

add_subdirectory("source_subfolder")
