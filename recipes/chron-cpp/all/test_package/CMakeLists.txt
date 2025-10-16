cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(chron-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE oryx::chron-cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
