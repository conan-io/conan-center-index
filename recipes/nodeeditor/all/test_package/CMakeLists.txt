cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(QtNodes CONFIG REQUIRED)

add_executable(${PROJECT_NAME}  main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE QtNodes::QtNodes)
