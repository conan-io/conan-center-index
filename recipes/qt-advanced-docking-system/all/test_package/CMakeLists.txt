cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(qt-advanced-docking-system REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example qt-advanced-docking-system::qt-advanced-docking-system)
target_compile_features(example PRIVATE cxx_std_17)
