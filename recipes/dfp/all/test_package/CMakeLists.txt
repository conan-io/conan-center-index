cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(dfp CONFIG REQUIRED)


add_executable(${PROJECT_NAME} src/demo.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dfp::dfp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
