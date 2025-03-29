cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(resultlib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

find_path(RESULTLIB_INCLUDE_DIR "resultlib/result.h")
target_include_directories(${PROJECT_NAME} PRIVATE ${RESULTLIB_INCLUDE_DIR})
