cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include("${CMAKE_SOURCE_DIR}/../conanbuildinfo.cmake")
conan_basic_setup()

include("CMakeListsOriginal.txt")
