cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(darknet CONFIG REQUIRED)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} darknet::darknet)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
