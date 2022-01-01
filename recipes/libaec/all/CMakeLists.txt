cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")

if (MSVC)
    set (CMAKE_SHARED_LINKER_FLAGS "/INCREMENTAL:NO")
    set (CMAKE_STATIC_LINKER_FLAGS "/INCREMENTAL:NO")
endif()