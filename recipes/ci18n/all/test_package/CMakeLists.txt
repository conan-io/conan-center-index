cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(ci18n REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ci18n::ci18n)
