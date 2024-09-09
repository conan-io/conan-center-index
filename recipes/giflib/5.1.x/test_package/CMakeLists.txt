cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(GIF REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} GIF::GIF)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY C_STANDARD 99)
