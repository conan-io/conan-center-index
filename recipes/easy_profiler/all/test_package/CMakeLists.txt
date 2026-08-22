cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(easy_profiler REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE easy_profiler)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
