cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_definitions("-DHAVE_STDINT_H")
add_definitions("-DHAVE_SINF")

add_subdirectory("source_subfolder")
