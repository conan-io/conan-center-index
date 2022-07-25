cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(fatfs CONFIG REQUIRED)

add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE main.c)
target_link_libraries(${PROJECT_NAME} PRIVATE fatfs::fatfs)
