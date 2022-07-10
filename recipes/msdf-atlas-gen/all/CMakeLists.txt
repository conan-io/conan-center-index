cmake_minimum_required(VERSION 3.10)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(msdfgen REQUIRED)

add_subdirectory(source_subfolder)

