cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(cpp-sort REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} cpp-sort-integrity.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE cpp-sort::cpp-sort)
target_compile_features(${CMAKE_PROJECT_NAME} PRIVATE cxx_std_14)
