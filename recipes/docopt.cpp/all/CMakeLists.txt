cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

add_subdirectory("source_subfolder")
