cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(unity REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE unity::unity)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
