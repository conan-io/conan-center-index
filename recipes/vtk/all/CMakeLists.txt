cmake_minimum_required(VERSION 3.12...3.16 FATAL_ERROR)
project(cmake_wrapper)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_subdirectory("source_subfolder")
