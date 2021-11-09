cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS on)

add_subdirectory("source_subfolder")
