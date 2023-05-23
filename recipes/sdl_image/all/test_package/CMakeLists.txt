cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(SDL2_image REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET SDL2_image::SDL2_image-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2_image::SDL2_image-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2_image::SDL2_image)
endif()
