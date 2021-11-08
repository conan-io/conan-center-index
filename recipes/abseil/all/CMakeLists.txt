cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions("-D_HAS_DEPRECATED_RESULT_OF")
endif()

add_subdirectory(source_subfolder)
