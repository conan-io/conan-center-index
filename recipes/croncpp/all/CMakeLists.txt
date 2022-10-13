cmake_minimum_required(VERSION 3.1)
project(conan_wrapper CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)

add_subdirectory(source_subfolder)
