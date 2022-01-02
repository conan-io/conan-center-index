cmake_minimum_required(VERSION 2.8.11)

if (MSVC)
    set (CMAKE_SHARED_LINKER_FLAGS "/INCREMENTAL:NO")
    set (CMAKE_STATIC_LINKER_FLAGS "/INCREMENTAL:NO")
endif()
set( MSVC_INCREMENTAL_YES_FLAG "/INCREMENTAL:NO")

project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")

