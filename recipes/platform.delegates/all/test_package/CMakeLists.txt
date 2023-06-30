cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(platform.delegates REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} platform.delegates::platform.delegates)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17)
