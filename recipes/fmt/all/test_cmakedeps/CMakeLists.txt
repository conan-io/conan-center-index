cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fmt REQUIRED CONFIG)

# TEST_PACKAGE #################################################################
add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 14)
if(FMT_HEADER_ONLY)
    target_link_libraries(${CMAKE_PROJECT_NAME} fmt::fmt-header-only)
else()
    target_link_libraries(${CMAKE_PROJECT_NAME} fmt::fmt)
endif()

# TEST_RANGES ##################################################################
add_executable(test_ranges test_ranges.cpp)
set_property(TARGET test_ranges PROPERTY CXX_STANDARD 14)
if(FMT_HEADER_ONLY)
    target_link_libraries(test_ranges fmt::fmt-header-only)
else()
    target_link_libraries(test_ranges fmt::fmt)
endif()
