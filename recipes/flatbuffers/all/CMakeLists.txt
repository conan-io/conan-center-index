cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (WIN32 AND MSVC AND FLATBUFFERS_BUILD_SHAREDLIB)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif(WIN32 AND MSVC AND FLATBUFFERS_BUILD_SHAREDLIB)

add_subdirectory("source_subfolder")
