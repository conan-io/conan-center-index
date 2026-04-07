cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(NekoSchema REQUIRED CONFIG)

add_executable(conan_test test_package.cpp)
target_link_libraries(conan_test PRIVATE Neko::Schema)
