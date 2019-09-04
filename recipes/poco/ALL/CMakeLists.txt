cmake_minimum_required(VERSION 2.8.12)
PROJECT(conancmakewrapper)

message(STATUS "Conan CMake Wrapper")
include("${CMAKE_CURRENT_SOURCE_DIR}/../conanbuildinfo.cmake")
CONAN_BASIC_SETUP()

include("CMakeListsOriginal.cmake")
