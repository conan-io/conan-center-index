cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(jemalloc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_compile_definitions(${PROJECT_NAME} PRIVATE JEMALLOC_MANGLE)
target_link_libraries(${PROJECT_NAME} PRIVATE jemalloc::jemalloc)
