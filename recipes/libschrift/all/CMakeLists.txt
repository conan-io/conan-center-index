cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper LANGUAGES C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_EXTENSIONS OFF)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include_directories(source_subfolder)

add_library(schrift source_subfolder/schrift.c)
