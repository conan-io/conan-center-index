cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(systemc-cci REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} systemc-cci::systemc-cci)
