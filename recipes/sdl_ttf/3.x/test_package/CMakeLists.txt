cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(SDL3_ttf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET SDL3_ttf::SDL3_ttf)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL3_ttf::SDL3_ttf)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL3_ttf::SDL3_ttf-static)
endif()
