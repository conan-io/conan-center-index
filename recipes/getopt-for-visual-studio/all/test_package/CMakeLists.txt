cmake_minimum_required(VERSION 3.0)
project(test_package LANGUAGES C)

find_package(getopt-for-visual-studio)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE getopt-for-visual-studio::getopt-for-visual-studio)
