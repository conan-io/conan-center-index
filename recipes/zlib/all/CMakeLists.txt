cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

cmake_policy(SET CMP0091 NEW)
include(conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CMAKE_SOURCE_DIR}/source_subfolder)
add_subdirectory("source_subfolder")
