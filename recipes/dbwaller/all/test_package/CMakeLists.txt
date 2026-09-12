cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(DBWaller CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_compile_features(example PRIVATE cxx_std_20)
target_link_libraries(example PRIVATE DBWaller::dbwaller)
