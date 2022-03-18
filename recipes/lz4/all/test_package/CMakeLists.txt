cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(lz4 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} lz4::lz4)

option(TEST_SHARED_LIB "Use package in a shared library")
if(TEST_AS_SHARED_LIB)
    add_library(${PROJECT_NAME}2 SHARED lib.c)
    target_link_libraries(${PROJECT_NAME}2 lz4::lz4)
endif()
