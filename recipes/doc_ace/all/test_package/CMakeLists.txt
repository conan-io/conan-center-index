cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

# Prefer to use found static libraries
set(CMAKE_FIND_LIBRARY_SUFFIXES .a ${CMAKE_FIND_LIBRARY_SUFFIXES})

find_package(doc_ace REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE doc_ace::doc_ace)

