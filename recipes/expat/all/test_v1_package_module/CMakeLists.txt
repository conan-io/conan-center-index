cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package_module/
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package_module/)
