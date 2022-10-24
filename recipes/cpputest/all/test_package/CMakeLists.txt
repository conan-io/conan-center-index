cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(CppUTest REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE CppUTest)

if(WITH_EXTENSIONS)
    add_executable(test_package_with_extensions test_package_with_extensions.cpp)
    target_link_libraries(test_package_with_extensions PRIVATE CppUTestExt)
endif()
