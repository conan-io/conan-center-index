cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(cenginel REQUIRED CONFIG)
find_package(Eigen3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cenginel::cenginel Eigen3::Eigen)
