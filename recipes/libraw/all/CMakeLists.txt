cmake_minimum_required(VERSION 3.1)
project(LibRaw)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(cmake_subfolder)
