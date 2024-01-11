cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(cpp_project_framework REQUIRED CONFIG)
find_package(GTest REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE cpp_project_framework::cpp_project_framework GTest::gtest GTest::gtest_main)
if(UNIX)
	target_link_libraries(test_package PRIVATE stdc++fs)
endif()
