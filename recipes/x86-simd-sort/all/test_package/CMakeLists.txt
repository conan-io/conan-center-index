cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(x86-simd-sort REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE x86-simd-sort::x86-simd-sort)
