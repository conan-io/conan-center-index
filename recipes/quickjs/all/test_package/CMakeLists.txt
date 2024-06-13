cmake_minimum_required(VERSION 3.0)
project(test_package LANGUAGES C)

find_package(quickjs REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE quickjs::quickjs)
