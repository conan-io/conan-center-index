cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(harfbuzz REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} harfbuzz::harfbuzz)
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
