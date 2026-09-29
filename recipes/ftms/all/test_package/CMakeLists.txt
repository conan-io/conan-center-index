cmake_minimum_required(VERSION 3.16)
project(ftms_test_package LANGUAGES C CXX)

find_package(ftms CONFIG REQUIRED)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c PRIVATE ftms::ftms)
add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp PRIVATE ftms::ftms)
target_compile_features(test_package_cpp PRIVATE cxx_std_11)
