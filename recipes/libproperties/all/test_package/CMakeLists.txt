cmake_minimum_required(VERSION 3.1)
project(libproperties_test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(libproperties_test_package test_package.c)
target_link_libraries(libproperties_test_package ${CONAN_LIBS})
