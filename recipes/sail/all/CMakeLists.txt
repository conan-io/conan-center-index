cmake_minimum_required(VERSION 3.10)
project(cmake_wrapper C CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_subdirectory(src)
