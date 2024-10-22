cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(PkgConfig)
pkg_check_modules(TREE_SITTER_SQL REQUIRED "tree-sitter-sql")

add_executable(${PROJECT_NAME} test_package.c)
target_include_directories(${PROJECT_NAME} PUBLIC ${TREE_SITTER_SQL_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PUBLIC ${TREE_SITTER_SQL_LDFLAGS})
