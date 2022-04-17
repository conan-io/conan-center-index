cmake_minimum_required(VERSION 3.1.3)
project(PclTestPackage)

find_package(PCL REQUIRED surface CONFIG)

add_executable(pcl_test_package example.cpp)
target_compile_features(pcl_test_package PUBLIC cxx_std_14)
target_link_libraries(pcl_test_package PRIVATE PCL_SURFACE_LIBRARIES)
