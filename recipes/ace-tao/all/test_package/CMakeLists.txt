cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)


set(CMAKE_FIND_LIBRARY_SUFFIXES ${CMAKE_FIND_LIBRARY_SUFFIXES})

find_package(ace-tao REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ace-tao::ace-tao)

