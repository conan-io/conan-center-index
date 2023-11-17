cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)

find_package(dfp CONFIG REQUIRED)


add_executable(${PROJECT_NAME} src/demo.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dfp::dfp)
