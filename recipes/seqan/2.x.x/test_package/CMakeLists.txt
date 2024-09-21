cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(seqan REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE seqan::seqan)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
