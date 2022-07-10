cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD 11)

find_package(pybind11_json REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PUBLIC pybind11_json::pybind11_json)  # FIXME: target should be pybind11_json
