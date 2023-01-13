cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(svt-av1 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE svt-av1::encoder)
target_link_libraries(${PROJECT_NAME} PRIVATE svt-av1::decoder)
