cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(out_ptr CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package out_ptr::out_ptr)
target_compile_features(test_package PRIVATE cxx_std_11)

enable_testing()
add_test(NAME test_package
         COMMAND test_package)
