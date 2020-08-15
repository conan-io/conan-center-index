cmake_minimum_required(VERSION 2.8.12)
project(r8brain-free-src CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(r8brain r8brain-free-src/r8bbase.cpp)