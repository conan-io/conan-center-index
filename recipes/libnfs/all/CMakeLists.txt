cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

set(CMAKE_VERBOSE_MAKEFILE ON)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_subdirectory(source_subfolder)
