cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(HighFive REQUIRED CONFIG)

add_executable(test_package test_package.cpp)

if (${HighFive_VERSION} VERSION_LESS 3.0.0)
    target_link_libraries(test_package PRIVATE HighFive)
    target_compile_features(test_package PRIVATE cxx_std_11)
else()
    target_link_libraries(test_package PRIVATE HighFive::HighFive)
    target_compile_features(test_package PRIVATE cxx_std_14)
endif()
