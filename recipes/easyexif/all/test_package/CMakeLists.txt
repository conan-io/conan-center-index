cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX) # if the project uses c++

find_package(easyexif REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE easyexif::easyexif)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
