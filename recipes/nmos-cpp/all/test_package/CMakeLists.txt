cmake_minimum_required(VERSION 3.1)
project(NmosCppTestPackage CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(nmos-cpp REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package nmos-cpp::compile-settings nmos-cpp::nmos-cpp)
set_target_properties(test_package PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED ON)
