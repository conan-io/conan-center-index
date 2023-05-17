cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C) # if the project is pure C
# project(test_package LANGUAGES CXX) # if the project uses c++

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(package REQUIRED CONFIG)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package/
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package/)
