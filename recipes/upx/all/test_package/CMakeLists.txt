cmake_minimum_required(VERSION 3.15)
project(test_package C)

if(CMAKE_C_COMPILER_ID MATCHES "AppleClang|Clang|GNU")
    add_link_options(-static)
endif()

add_executable(${PROJECT_NAME} test_package.c)
