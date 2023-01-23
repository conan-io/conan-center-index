cmake_minimum_required(VERSION 3.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory("${CMAKE_SOURCE_DIR}/../test_package" "${CMAKE_BINARY_DIR}/test_package")
