cmake_minimum_required(VERSION 3.21.0)
project(testcpp LANGUAGES CXX)

add_executable(testcpp test.cpp)
target_link_libraries(testcpp daggy::daggy)
