cmake_minimum_required(VERSION 3.0)
project(test_package CXX)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME})
