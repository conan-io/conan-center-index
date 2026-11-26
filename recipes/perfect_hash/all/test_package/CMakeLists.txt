cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(perfect_hash REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ConstexprCore::perfect_hash)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
