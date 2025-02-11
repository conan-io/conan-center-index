cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(qt6advanceddocking REQUIRED CONFIG)
find_package(Qt6 REQUIRED)
add_executable(example example.cpp)
target_link_libraries(example ads::qt6advanceddocking Qt6::Core)
