cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(icu4x REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE icu4x::icu4x)

add_executable(${PROJECT_NAME}_cpp test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cpp PRIVATE icu4x::icu4x)
