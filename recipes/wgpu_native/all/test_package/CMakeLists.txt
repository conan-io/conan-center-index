cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(wgpu_native REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE wgpu_native::wgpu_native)
