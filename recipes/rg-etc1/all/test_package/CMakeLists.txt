cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(rg-etc1 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE rg-etc1::rg-etc1)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
