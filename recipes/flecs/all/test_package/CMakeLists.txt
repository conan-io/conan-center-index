cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(flecs REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET flecs::flecs_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE flecs::flecs_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE flecs::flecs)
endif()
