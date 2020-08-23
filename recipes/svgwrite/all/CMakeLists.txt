cmake_minimum_required(VERSION 2.8.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif(WIN32 AND BUILD_SHARED_LIBS)

add_subdirectory("source_subfolder")