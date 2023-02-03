cmake_minimum_required(VERSION 3.11)
project(jungle)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory("source_subfolder")
