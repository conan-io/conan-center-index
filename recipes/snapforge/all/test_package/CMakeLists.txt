cmake_minimum_required(VERSION 3.20)
project(snapforge_conan_test LANGUAGES CXX)

find_package(SnapForge CONFIG REQUIRED)
add_executable(test_package test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_17)
target_link_libraries(test_package PRIVATE SnapForge::snapforge)
