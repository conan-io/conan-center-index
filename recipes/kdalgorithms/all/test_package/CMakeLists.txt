cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(KDAlgorithms REQUIRED CONFIG)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE KDAB::kdalgorithms)
