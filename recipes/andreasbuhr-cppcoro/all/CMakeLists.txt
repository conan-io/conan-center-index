cmake_minimum_required(VERSION 3.0)
project(cppcoro CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
