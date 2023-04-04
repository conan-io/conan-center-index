cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)


set(SOURCES test_package.c)

find_package(egl REQUIRED)

add_executable(${PROJECT_NAME} ${SOURCES})
target_link_libraries(${PROJECT_NAME} PRIVATE egl::egl)
