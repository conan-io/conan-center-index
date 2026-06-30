cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(RmlUi REQUIRED CONFIG)
add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE RmlUi::RmlUi)
