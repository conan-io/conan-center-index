cmake_minimum_required(VERSION 3.13)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()

add_subdirectory("source_subfolder")
