cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(tree-sitter-c REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE tree-sitter-c::tree-sitter-c)
if(tree-sitter-c_VERSION VERSION_LESS "0.23.2")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TREE_SITTER_C_API_H)
endif()