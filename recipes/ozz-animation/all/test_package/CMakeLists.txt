cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ozz-animation REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD_REQUIRED ON)
target_link_libraries(${PROJECT_NAME} PRIVATE ozz-animation::ozz-animation)
