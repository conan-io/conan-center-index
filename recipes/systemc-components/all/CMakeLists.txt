cmake_minimum_required(VERSION 3.15)
project(scc)

include(${CMAKE_CURRENT_SOURCE_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(scc)
