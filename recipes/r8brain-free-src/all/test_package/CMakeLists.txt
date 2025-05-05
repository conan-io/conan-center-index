cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(r8brain-free-src REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE r8brain-free-src::r8brain-free-src)
