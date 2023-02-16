cmake_minimum_required(VERSION 3.8)
project(test_package CXX)
set(CMAKE_CXX_STANDARD 11)

find_package(minisat REQUIRED CONFIG)
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE minisat::minisat)
