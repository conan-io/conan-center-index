cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(gcem CONFIG REQUIRED)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE gcem::gcem)
target_compile_features(${CMAKE_PROJECT_NAME} PRIVATE cxx_std_11)
