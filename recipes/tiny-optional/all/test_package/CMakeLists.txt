cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(tiny-optional REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE tiny-optional::tiny-optional)

# Some features are not available for non-x86 architectures
if(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "x86")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TINY_OPTIONAL_x86)
elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "x86_64")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TINY_OPTIONAL_x64)
endif()
