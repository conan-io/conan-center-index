cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(godot-cpp REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE godot-cpp::godot-cpp)
set_property(TARGET test_package PROPERTY CXX_STANDARD 17)
set_property(TARGET test_package PROPERTY CXX_STANDARD_REQUIRED ON)
