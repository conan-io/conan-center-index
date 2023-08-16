cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(earcut REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE earcut::earcut)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
