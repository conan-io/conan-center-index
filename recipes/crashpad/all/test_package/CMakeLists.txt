cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(crashpad REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE crashpad::crashpad)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
