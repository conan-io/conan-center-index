cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(SDL3_net REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

if(TARGET SDL3_net::SDL3_net)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL3_net::SDL3_net)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL3_net::SDL3_net-static)
endif()
