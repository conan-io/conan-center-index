cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(re2 REQUIRED CONFIG)

add_subdirectory(source_subfolder/)
