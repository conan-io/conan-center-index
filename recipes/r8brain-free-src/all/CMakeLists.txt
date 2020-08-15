cmake_minimum_required(VERSION 3.1)
project(r8brain-free-src CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(r8brain source_subfolder/r8bbase.cpp)
