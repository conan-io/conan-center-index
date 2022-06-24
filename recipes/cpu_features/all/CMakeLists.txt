cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_subdirectory("source_subfolder")
