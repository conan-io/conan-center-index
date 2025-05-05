cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(id3v2lib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE id3v2lib::id3v2lib)
