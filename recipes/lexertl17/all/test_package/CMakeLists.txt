cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(lexertl17 REQUIRED CONFIG)

add_executable(example example.cpp)

target_link_libraries(example PRIVATE lexertl17::lexertl17)
