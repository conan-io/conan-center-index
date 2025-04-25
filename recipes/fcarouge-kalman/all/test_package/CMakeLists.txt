cmake_minimum_required(VERSION 3.25)
project(test_package LANGUAGES CXX)

find_package(fcarouge-kalman REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fcarouge-kalman::kalman)
