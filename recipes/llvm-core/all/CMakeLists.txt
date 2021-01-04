cmake_minimum_required(VERSION 3.4.3)
project(conanllvm)

include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source")
