cmake_minimum_required(VERSION 3.22.0)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

enable_testing()
add_subdirectory("source_subfolder/src")
