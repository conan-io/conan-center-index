cmake_minimum_required(VERSION 3.8)

project(test_package C) # if the project is pure C

find_package(ghostscript REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ghostscript::ghostscript)
