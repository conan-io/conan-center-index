cmake_minimum_required(VERSION 3.21)
project(test_package LANGUAGES CXX)

find_package(gapp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE gapp::gapp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
