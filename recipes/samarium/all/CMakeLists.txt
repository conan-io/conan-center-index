cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_CURRENT_SOURCE_DIR})

add_subdirectory(source_subfolder/src)
