cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(flex CONFIG REQUIRED)

add_executable(${PROJECT_NAME} basic_nr.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE flex::flex)

add_executable(test_yywrap test_yywrap.c)
target_link_libraries(test_yywrap PRIVATE flex::flex)
