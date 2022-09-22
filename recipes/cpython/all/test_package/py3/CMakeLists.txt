cmake_minimum_required(VERSION 3.15)

project(test_package C) # if the project is pure C

find_package(Python REQUIRED COMPONENTS Interpreter Development)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Python::Python)
