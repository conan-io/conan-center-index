cmake_minimum_required(VERSION 3.4.3)
project(ParallelSTLPackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(pstl_test_package main.cpp)
target_compile_features(pstl_test_package PRIVATE cxx_std_11)
find_package(ParallelSTL)
target_link_libraries(pstl_test_package PRIVATE ParallelSTL::ParallelSTL)
