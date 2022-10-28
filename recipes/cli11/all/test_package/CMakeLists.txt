cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(CLI11 REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE CLI11::CLI11)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
