cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(source_subfolder)
