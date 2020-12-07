cmake_minimum_required(VERSION 3.14)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

message(STATUS !!!!!!!!!!!!!! CMAKE_CURRENT_SOURCE_DIR = ${CMAKE_CURRENT_SOURCE_DIR})

add_subdirectory(source_subfolder/logr)
