cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(aws-c-cal REQUIRED CONFIG)
find_package(aws-c-common REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE AWS::aws-c-cal AWS::aws-c-common)
