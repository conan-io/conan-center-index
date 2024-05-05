cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_program(RE2C NAMES re2c)

add_custom_command(OUTPUT test_package.c
    COMMAND "${RE2C}" -W "${CMAKE_CURRENT_LIST_DIR}/syntax.re" -I "$ENV{RE2C_STDLIB_DIR}" -o test_package.c
)

add_executable(${PROJECT_NAME} test_package.c)
