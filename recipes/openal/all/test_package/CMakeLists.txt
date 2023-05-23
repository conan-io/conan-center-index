cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(OpenAL REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE OpenAL::OpenAL)
