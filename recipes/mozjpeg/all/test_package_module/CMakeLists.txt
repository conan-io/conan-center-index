cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(JPEG REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE JPEG::JPEG)
