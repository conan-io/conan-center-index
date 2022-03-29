cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

if (WITH_OPENEXR)
    set(CMAKE_CXX_STANDARD 11)
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})
include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_subdirectory("source_subfolder")
