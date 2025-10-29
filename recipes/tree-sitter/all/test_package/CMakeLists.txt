cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(tree-sitter REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} tree-sitter::tree-sitter)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
