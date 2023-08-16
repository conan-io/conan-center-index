cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(OpenCV REQUIRED core CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE opencv_core)
