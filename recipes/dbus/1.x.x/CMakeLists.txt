cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(../conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("cmake")
