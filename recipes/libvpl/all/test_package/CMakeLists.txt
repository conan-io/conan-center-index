cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(VPL REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE VPL::dispatcher)

add_executable(test_c test_c.c)
target_link_libraries(test_c PRIVATE VPL::dispatcher)
