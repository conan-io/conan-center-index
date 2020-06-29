cmake_minimum_required(VERSION 3.0)
project(conan_glew)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()
include(GNUInstallDirs)

add_subdirectory("source_subfolder/build/cmake")
