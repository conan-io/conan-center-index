cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(miniaudio REQUIRED)

add_executable(${PROJECT_NAME} example.c)
target_link_libraries(${PROJECT_NAME} miniaudio::miniaudio)
