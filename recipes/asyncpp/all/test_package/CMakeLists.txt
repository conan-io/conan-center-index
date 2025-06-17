cmake_minimum_required(VERSION 3.15)
project(TestPackage LANGUAGES CXX)

find_package(asyncpp CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package asyncpp::asyncpp)
target_compile_features(test_package PUBLIC cxx_std_20)
