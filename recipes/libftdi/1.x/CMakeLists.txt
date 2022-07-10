cmake_minimum_required(VERSION 2.8)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
add_subdirectory(source_subfolder)
