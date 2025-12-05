cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(xenium REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE xenium::xenium)
