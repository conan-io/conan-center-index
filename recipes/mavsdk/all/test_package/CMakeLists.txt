cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(MAVSDK REQUIRED)

add_executable(test_pkg test_package.cpp)
target_link_libraries(test_pkg PRIVATE MAVSDK::MAVSDK)
