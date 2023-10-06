cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(fast_io REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fast_io::fast_io)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
