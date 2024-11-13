cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(async_simple REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(ASYNC_SIMPLE_HEADER_ONLY)
    target_link_libraries(test_package PRIVATE async_simple::async_simple_header_only)
else()
    target_link_libraries(test_package PRIVATE async_simple::async_simple)
endif()
