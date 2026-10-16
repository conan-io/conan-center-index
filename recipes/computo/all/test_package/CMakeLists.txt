cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(computo REQUIRED)
find_package(nlohmann_json REQUIRED)

add_executable(test_package src/example.cpp)
target_link_libraries(test_package computo::computo nlohmann_json::nlohmann_json)
target_compile_features(test_package PRIVATE cxx_std_17)