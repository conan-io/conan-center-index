cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(fmt REQUIRED CONFIG)

# TEST_PACKAGE #################################################################

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} CONAN_PKG::fmt)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 14)

if (FMT_HEADER_ONLY)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE FMT_HEADER_ONLY=1)
endif(FMT_HEADER_ONLY)

# TEST_RANGES ##################################################################
add_executable(test_ranges test_ranges.cpp)
target_link_libraries(test_ranges CONAN_PKG::fmt)
set_property(TARGET test_ranges PROPERTY CXX_STANDARD 14)

if (FMT_HEADER_ONLY)
    target_compile_definitions(test_ranges PRIVATE FMT_HEADER_ONLY=1)
endif(FMT_HEADER_ONLY)
