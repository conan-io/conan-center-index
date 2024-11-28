cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(PkgConfig)
pkg_check_modules(TREE_SITTER_SQL IMPORTED_TARGET "tree-sitter-sql")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::TREE_SITTER_SQL)
if(TREE_SITTER_SQL_VERSION VERSION_LESS "0.3.7")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TREE_SITTER_SQL_OLD_PATH)
endif()

