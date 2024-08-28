cmake_minimum_required(VERSION 3.2.0)
project(test_package LANGUAGES CXX)

find_package(level-zero CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE level-zero::level-zero)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)