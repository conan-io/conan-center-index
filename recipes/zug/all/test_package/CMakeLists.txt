cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(zug CONFIG REQUIRED)

add_executable(test_package example.cpp)
target_link_libraries(test_package zug::zug)
set_target_properties(test_package PROPERTIES CXX_STANDARD 14)
