cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(cantera REQUIRED)

add_executable(test_package test_package.cpp)

if(CMAKE_DL_LIBS)
    target_link_libraries(test_package PRIVATE ${CMAKE_DL_LIBS})
endif()

target_link_libraries(test_package PUBLIC cantera::cantera)
target_compile_features(test_package PRIVATE cxx_std_17)
