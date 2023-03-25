cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(fastgltf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} fastgltf::fastgltf)
