cmake_minimum_required(VERSION 3.8)
project(test_package CXX)
set(CMAKE_CXX_STANDARD 14)

find_package(soplex REQUIRED CONFIG)
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE soplex::soplex)
