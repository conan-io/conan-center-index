cmake_minimum_required(VERSION 3.15)
project(test_v1_package)

enable_testing()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package)
