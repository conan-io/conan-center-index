cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package)
