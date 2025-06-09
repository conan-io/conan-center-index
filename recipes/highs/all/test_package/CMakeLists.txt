cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(highs REQUIRED CONFIG)
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE highs::highs)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
