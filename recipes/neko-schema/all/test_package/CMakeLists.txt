cmake_minimum_required(VERSION 3.14)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(NekoSchema REQUIRED CONFIG)

add_executable(conan_test test_package.cpp)
target_link_libraries(conan_test PRIVATE Neko::Schema)
