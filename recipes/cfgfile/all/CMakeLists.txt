cmake_minimum_required(VERSION 3.10)
project(cmake_wrapper)

set(CMAKE_CXX_STANDARD 14)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
