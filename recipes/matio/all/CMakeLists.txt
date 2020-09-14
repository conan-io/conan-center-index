cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)
message(STATUS "The CMake version is ${CMAKE_VERSION}")

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
