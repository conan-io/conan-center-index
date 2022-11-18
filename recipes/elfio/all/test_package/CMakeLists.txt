cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(elfio REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE elfio::elfio)
target_compile_features(example PRIVATE cxx_std_14)
