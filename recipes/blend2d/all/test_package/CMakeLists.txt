cmake_minimum_required(VERSION 3.8)
project(PackageTest CXX)

find_package(blend2d CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package blend2d::blend2d)
target_compile_features(test_package PRIVATE cxx_std_11)
