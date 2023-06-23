cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(logr REQUIRED)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} logr::logr)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
