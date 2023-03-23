cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(msgpack REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET msgpackc)
    target_link_libraries(${PROJECT_NAME} PRIVATE msgpackc)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE msgpack-c)
endif()
