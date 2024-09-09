cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(SI REQUIRED CONFIG)

add_executable(${PROJECT_NAME} si_package_test.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_link_libraries(${PROJECT_NAME} SI::SI)
