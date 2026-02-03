cmake_minimum_required(VERSION 3.20)
project(PackageTest CXX)

find_package(loon REQUIRED)

add_executable(test_package src/test_package.cpp)
target_link_libraries(test_package PRIVATE loon::loon)
target_compile_features(test_package PRIVATE cxx_std_23)
