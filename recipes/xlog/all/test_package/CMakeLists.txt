cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(xlog REQUIRED)

add_executable(test test.cpp)
target_link_libraries(test PRIVATE xlog::xlog)
