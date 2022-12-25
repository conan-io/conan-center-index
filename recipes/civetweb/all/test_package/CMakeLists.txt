cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(civetweb REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} civetweb::civetweb)
