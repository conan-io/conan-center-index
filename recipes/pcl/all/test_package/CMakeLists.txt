cmake_minimum_required(VERSION 3.1.3)
project(PclTestPackage)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PCL)

add_executable(pcl_test_package example.cpp)
target_compile_features(pcl_test_package PUBLIC cxx_std_14)
target_link_libraries(pcl_test_package PRIVATE PCL::PCL_SURFACE_LIBRARIES)
