project(vigra_conan_test)
cmake_minimum_required(VERSION 3.20)

find_package(Vigra REQUIRED)

add_executable(test_package main.cpp)
target_link_libraries(test_package vigraimpex)
