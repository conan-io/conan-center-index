cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(tcb-span REQUIRED)

add_executable(test_package test_package.cxx)
target_link_libraries(test_package tcb-span::tcb-span)
set_property(TARGET test_package PROPERTY CXX_STANDARD 17)
