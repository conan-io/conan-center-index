cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(DuckDB REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# you can still use duckdb::duckdb as the global target
if(NOT TARGET duckdb_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE duckdb)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE duckdb_static)
endif()
