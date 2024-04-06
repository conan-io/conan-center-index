cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)

find_package(pybind11_json REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
 # FIXME: target should be pybind11_json, replace once Conan v1 has been dropped
target_link_libraries(test_package PUBLIC pybind11_json::pybind11_json)
