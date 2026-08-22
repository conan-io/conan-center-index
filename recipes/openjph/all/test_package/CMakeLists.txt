cmake_minimum_required(VERSION 3.11)
project(test_package LANGUAGES CXX)

find_package(openjph REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE openjph::openjph)
