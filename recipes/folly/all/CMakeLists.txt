cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_compile_options(/std:c++latest /permissive-)
endif()

add_subdirectory(source_subfolder)
