cmake_minimum_required(VERSION 3.15)
project(gdal_cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
