cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(lexbor REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

if(TARGET lexbor::lexbor_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE lexbor::lexbor_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE lexbor::lexbor)
endif()
