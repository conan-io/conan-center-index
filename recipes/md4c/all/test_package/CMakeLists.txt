cmake_minimum_required(VERSION 3.8)

project(test_package C)

find_package(md4c CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(test_package PRIVATE md4c::md4c)
