cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(CppUTest REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package CppUTest::CppUTest)

if(WITH_EXTENSIONS)
    add_executable(test_package_with_extensions test_package_with_extensions.cpp)
    # Note: CppUTest::CppUTestExt adds dependency on CppUTest::CppUTest
    target_link_libraries(test_package_with_extensions CppUTest::CppUTestExt)
endif()
