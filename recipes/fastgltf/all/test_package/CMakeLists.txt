cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(fastgltf REQUIRED CONFIG)

set(CMAKE_CXX_STANDARD 17)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} fastgltf::fastgltf)
