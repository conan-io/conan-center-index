cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(BuildUtils.cmake)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(source_subfolder)
