cmake_minimum_required(VERSION 3.21.0)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory("source_subfolder/src")
