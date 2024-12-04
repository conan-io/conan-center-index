cmake_minimum_required(VERSION 3.28)
project(test_package LANGUAGES C)

find_package(logging REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE logging::logging)