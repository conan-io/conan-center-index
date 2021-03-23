cmake_minimum_required(VERSION 3.1)
project(coz)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
