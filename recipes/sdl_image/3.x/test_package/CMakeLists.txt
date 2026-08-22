cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(SDL3_image REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET SDL3_image::SDL3_image-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL3_image::SDL3_image-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL3_image::SDL3_image)
endif()
