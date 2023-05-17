cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_custom_command(OUTPUT test_package.c
    COMMAND re2c -W "${PROJECT_SOURCE_DIR}/syntax.re" -o test_package.c
)

add_executable(${PROJECT_NAME} test_package.c)
