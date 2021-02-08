cmake_minimum_required(VERSION 3.10)
project(cmake_wrapper)

if (MSVC)
    add_compile_definitions("/EHsc")
endif()

add_subdirectory("source_subfolder")
