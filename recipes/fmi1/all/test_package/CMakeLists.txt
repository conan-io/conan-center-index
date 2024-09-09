cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(fmi1 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fmi1::cosim)
