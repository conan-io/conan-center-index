cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS)

add_subdirectory("source_subfolder")
