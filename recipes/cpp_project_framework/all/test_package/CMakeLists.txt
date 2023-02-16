cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cpp_project_framework REQUIRED)
find_package(GTest REQUIRED)

add_executable(test_package test_package.cpp)
if(UNIX)
	target_link_libraries(test_package cpp_project_framework::cpp_project_framework GTest::gtest GTest::gtest_main stdc++fs)
else()
	target_link_libraries(test_package cpp_project_framework::cpp_project_framework GTest::gtest GTest::gtest_main)
endif()
