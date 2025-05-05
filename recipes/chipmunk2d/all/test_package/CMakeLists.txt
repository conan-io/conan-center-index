cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(chipmunk2d REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE chipmunk2d::chipmunk2d)
