cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(certify REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE certify::core)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
