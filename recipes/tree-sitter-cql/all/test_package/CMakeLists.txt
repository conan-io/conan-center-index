cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(PkgConfig)
pkg_check_modules(TREE_SITTER_CQL IMPORTED_TARGET "tree-sitter-cql")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::TREE_SITTER_CQL)
