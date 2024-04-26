cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 14)

find_package(thorvg REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE thorvg::thorvg)
