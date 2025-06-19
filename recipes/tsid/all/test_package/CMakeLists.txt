cmake_minimum_required(VERSION 3.22)

project(test_package CXX)

find_package(tsid REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} tsid::tsid)
