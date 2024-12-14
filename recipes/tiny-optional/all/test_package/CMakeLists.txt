cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(tiny-optional REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE tiny-optional::tiny-optional)

# Some features are not available for non-x86 architectures
if(NOT ${CMAKE_SYSTEM_PROCESSOR} MATCHES "x86")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TINY_OPTIONAL_USE_SEPARATE_BOOL_INSTEAD_OF_UNUSED_BITS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE TINY_OPTIONAL_USE_SEPARATE_BOOL_INSTEAD_OF_MEMBER)
endif()
