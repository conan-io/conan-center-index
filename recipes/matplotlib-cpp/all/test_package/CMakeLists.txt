cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(matplotlib_cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE matplotlib_cpp::matplotlib_cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
