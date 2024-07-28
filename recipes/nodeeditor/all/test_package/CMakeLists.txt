cmake_minimum_required(VERSION 3.20)
project(test_qtnodes)

find_package(QtNodes REQUIRED)
add_executable(test_package  main.cpp)
target_link_libraries(test_package QtNodes::QtNodes)
