cmake_minimum_required(VERSION 3.3.0)
project(test_package LANGUAGES C)

find_package(mpfr REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE mpfr::mpfr)
