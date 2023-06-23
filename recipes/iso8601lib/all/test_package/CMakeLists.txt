cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(iso8601lib REQUIRED CONFIG)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE iso8601lib::iso8601lib)
