cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCLHeadersCpp REQUIRED CONFIG)

add_library(${PROJECT_NAME} OBJECT test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE OpenCL::HeadersCpp)

if(OpenCLHeadersCpp_VERSION VERSION_GREATER 2020.06.16)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_OPENCL_HPP)
endif()
