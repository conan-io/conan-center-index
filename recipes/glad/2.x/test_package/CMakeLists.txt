cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES C)

find_package(glad REQUIRED CONFIG)
find_package(glfw3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE glad::glad glfw)
