cmake_minimum_required(VERSION 3.22)
project(PackageTest CXX)

find_package(hashlib CONFIG REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package hashlib::hashlib)