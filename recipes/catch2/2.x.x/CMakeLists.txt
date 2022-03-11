cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(enable_benchmark "Enable benchmark" OFF)

if (enable_benchmark)
    add_definitions(-DCATCH_CONFIG_ENABLE_BENCHMARKING)
endif()

add_subdirectory(source_subfolder)
