cmake_minimum_required(VERSION 3.27)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 23)

find_package(hycan REQUIRED)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE hycan::hycan)
