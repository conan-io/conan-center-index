cmake_minimum_required(VERSION 3.8)
project(cmake_wrapper)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
