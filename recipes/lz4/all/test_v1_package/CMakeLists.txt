cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(lz4 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
if(TARGET LZ4::lz4_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE LZ4::lz4_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE LZ4::lz4_shared)
endif()

option(TEST_SHARED_LIB "Use package in a shared library")
if(TEST_AS_SHARED_LIB)
    add_library(${PROJECT_NAME}2 SHARED ../test_package/lib.c)
    if(TARGET LZ4::lz4_static)
        target_link_libraries(${PROJECT_NAME}2 PRIVATE LZ4::lz4_static)
    else()
        target_link_libraries(${PROJECT_NAME}2 PRIVATE LZ4::lz4_shared)
    endif()
endif()
