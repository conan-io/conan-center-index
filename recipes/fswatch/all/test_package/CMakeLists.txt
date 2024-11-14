cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(fswatch REQUIRED CONFIG)
find_package(Threads REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fswatch::fswatch Threads::Threads)
