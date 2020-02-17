cmake_minimum_required(VERSION 2.8)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(PHYSX_CONAN_FPIC ON)

add_subdirectory("source_subfolder/physx/compiler/public")
