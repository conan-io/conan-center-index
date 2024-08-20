cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libqasm REQUIRED CONFIG)

add_executable(test_package "${CMAKE_CURRENT_SOURCE_DIR}/src/test_package.cpp")
target_compile_features(test_package PRIVATE cxx_std_20)
target_link_libraries(test_package PRIVATE libqasm::libqasm)
