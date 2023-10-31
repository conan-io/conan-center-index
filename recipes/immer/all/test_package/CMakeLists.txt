cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES CXX)

find_package(immer REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE immer::immer)
target_compile_features(test_package PRIVATE cxx_std_14)
