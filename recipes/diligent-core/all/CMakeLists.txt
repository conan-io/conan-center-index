cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(glslang)

add_subdirectory(source_subfolder)
