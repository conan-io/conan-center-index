cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper LANGUAGES CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
