cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(nng REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE nng::nng)
