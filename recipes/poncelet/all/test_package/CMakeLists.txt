cmake_minimum_required(VERSION 3.20)
project(poncelet_test_package LANGUAGES CXX)

find_package(poncelet CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE poncelet::poncelet)
