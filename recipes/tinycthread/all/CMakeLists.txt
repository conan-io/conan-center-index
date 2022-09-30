cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper C)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS KEEP_RPATHS)

set(CMAKE_C_STANDARD 11)

add_subdirectory(source_subfolder)
