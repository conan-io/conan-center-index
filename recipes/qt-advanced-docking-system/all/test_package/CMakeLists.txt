cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(qt-advanced-docking-system REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example qt-advanced-docking-system::qt-advanced-docking-system)
