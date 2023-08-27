cmake_minimum_required(VERSION 3.15)
project(test_package
  LANGUAGES CXX
)

find_package(mp-units CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE mp-units::mp-units)
target_compile_features(test_package PUBLIC cxx_std_20)
