cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(fast_double_parser REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} fast_double_parser::fast_double_parser)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
