cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(embedded_ringbuf_cpp CONFIG REQUIRED)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE embedded_ringbuf_cpp::embedded_ringbuf_cpp)
