cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(gperftools REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_indirect test_package_indirect.c)
target_link_libraries(${PROJECT_NAME}_indirect PRIVATE gperftools::tcmalloc_minimal)

add_executable(${PROJECT_NAME}_direct test_package_direct.c)
target_link_libraries(${PROJECT_NAME}_direct PRIVATE gperftools::tcmalloc_minimal)
