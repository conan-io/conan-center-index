cmake_minimum_required(VERSION 3.0)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.c)
target_link_libraries(test_package ${CONAN_LIBS})
