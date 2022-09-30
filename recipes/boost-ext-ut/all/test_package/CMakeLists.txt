cmake_minimum_required(VERSION 3.16)
project(test_package)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED yes)
set(CMAKE_CXX_EXTENSIONS no)

find_package(ut REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE boost::ut)
