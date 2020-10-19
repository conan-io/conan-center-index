cmake_minimum_required(VERSION 2.8)
project(conanvtk) # DO NOT SUBMIT!!! What is goal of this file? Is it correct name for project which it defines?

message(STATUS "Conan CMake Wrapper")
include(conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CMAKE_SOURCE_DIR}/source_subfolder)
add_subdirectory("source_subfolder")
