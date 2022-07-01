cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(hunspell REQUIRED CONFIG)

add_executable(test_package test_package.cxx)
target_link_libraries(test_package PRIVATE hunspell::hunspell)
