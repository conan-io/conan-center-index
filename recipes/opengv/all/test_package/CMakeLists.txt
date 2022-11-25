cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(opengv REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} opengv)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
