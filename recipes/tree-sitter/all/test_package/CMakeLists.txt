cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(tree-sitter REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} tree-sitter::tree-sitter)
if(tree-sitter_VERSION VERSION_LESS "0.21.0")
    target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
endif()
