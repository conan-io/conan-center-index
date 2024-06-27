cmake_minimum_required(VERSION 3.15)
project(TestPackage CXX)

add_executable(test_package test_package.cpp)

find_package(asyncpp CONFIG REQUIRED)
target_link_libraries(test_package asyncpp::asyncpp)
target_compile_features(test_package PUBLIC cxx_std_20)
