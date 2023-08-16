cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(libfuse REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libfuse::libfuse)
target_compile_definitions(${PROJECT_NAME} PRIVATE FUSE_USE_VERSION=34)
