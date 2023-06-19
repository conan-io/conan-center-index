cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(metis REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE metis::metis)
