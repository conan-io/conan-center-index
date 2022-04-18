cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

set(CMAKE_CXX_STANDARD 11)
add_subdirectory("source_subfolder")
