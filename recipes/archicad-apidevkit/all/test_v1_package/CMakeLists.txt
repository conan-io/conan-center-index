cmake_minimum_required(VERSION 3.8)

project(test_package CXX)


include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package/
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package/)
