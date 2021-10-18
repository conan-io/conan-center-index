cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

set(CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}")

add_subdirectory("source_subfolder")
