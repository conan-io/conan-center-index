cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(cpp-sort REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} cpp-sort-integrity.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} cpp-sort::cpp-sort)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 14)
