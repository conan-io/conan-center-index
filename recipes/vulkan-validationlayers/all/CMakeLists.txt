cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(NOT TARGET glslang)
    add_library(glslang INTERFACE) # fake target for upstream CMakeLists (glslang required by tests only)
endif()

find_package(SPIRV-Tools REQUIRED CONFIG)

add_subdirectory(source_subfolder)
