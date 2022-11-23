cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C) # if the project is pure C

find_package(websocket-parser REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE websocket-parser::websocket-parser)
