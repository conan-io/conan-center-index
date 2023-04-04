cmake_minimum_required(VERSION 3.2)
project(test_package LANGUAGES C)

find_program(LEMON_PROGRAM NAMES lemon)

add_custom_command(
    OUTPUT gram.c gram.h
    COMMAND ${LEMON_PROGRAM} -s "${PROJECT_SOURCE_DIR}/gram.y" -d"${PROJECT_BINARY_DIR}"
    BYPRODUCTS gram.out
)

add_executable(${PROJECT_NAME} gram.c)
