cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

add_subdirectory(source_subfolder)
