cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

add_subdirectory(source_subfolder)
