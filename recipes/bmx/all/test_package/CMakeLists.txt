cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(bmx REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME}  PRIVATE  bmx::bmx)
