PROJECT(conanzlib)
cmake_minimum_required(VERSION 2.8)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

include_directories(${CMAKE_SOURCE_DIR}/source_subfolder)
add_subdirectory(source_subfolder)
