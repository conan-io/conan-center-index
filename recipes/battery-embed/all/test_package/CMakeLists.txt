cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(battery-embed REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

b_embed(${PROJECT_NAME} test_package.cpp)
