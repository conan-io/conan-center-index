cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(p-ranav-glob REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE p-ranav-glob::p-ranav-glob)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
