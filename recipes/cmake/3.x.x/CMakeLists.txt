cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

cmake_policy(SET CMP0091 NEW)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
