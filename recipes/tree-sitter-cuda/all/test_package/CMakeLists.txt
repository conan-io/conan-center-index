cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)
set(CMAKE_C_STANDARD 99)

find_package(tree-sitter-cuda REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE tree-sitter-cuda::tree-sitter-cuda)
