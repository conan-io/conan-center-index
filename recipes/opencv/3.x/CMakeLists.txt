cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

# OpenEXR public headers require C++11
if (WITH_OPENEXR)
    set(CMAKE_CXX_STANDARD 11)
endif()

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
