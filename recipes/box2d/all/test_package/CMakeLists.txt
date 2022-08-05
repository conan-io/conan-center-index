cmake_minimum_required(VERSION 3.4)
project(test_package)

find_package(box2d)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package box2d::box2d)
