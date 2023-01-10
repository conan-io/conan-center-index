cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(toml11 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE toml11::toml11)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
