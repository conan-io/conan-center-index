cmake_minimum_required(VERSION 3.12)
project(test_package CXX)

find_package(wg21_linear_algebra REQUIRED CONFIG)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package/
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package/)