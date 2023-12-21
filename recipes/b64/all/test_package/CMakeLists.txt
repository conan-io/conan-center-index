cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(b64 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE b64::b64)
