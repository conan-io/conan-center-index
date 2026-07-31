cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(icey REQUIRED COMPONENTS base)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE icey::base)
