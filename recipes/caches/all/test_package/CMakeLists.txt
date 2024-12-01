cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(caches REQUIRED)
find_package(GTest REQUIRED)

add_executable(${PROJECT_NAME} test.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE gtest::gtest)
target_link_libraries(${PROJECT_NAME} PRIVATE caches::caches)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
