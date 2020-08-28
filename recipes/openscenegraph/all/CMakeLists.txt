cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)

if(APPLE)
    add_compile_definitions("GL_SILENCE_DEPRECATION")
endif()

add_subdirectory("source_subfolder")
