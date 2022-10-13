cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(wslay REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET wslay_shared)
    target_link_libraries(${PROJECT_NAME} PRIVATE wslay_shared)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE wslay)
endif()
