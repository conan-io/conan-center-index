cmake_minimum_required(VERSION 3.15)
project(test_otl CXX)

find_package(otl REQUIRED CONFIG)

add_executable(test_otl test_otl.cpp)
target_link_libraries(test_otl PRIVATE otl::otl)
target_compile_features(test_otl PRIVATE cxx_std_11)
