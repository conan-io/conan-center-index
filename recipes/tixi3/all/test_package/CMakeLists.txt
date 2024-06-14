cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(tixi3 REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE tixi3)
