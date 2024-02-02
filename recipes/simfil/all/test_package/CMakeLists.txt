cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(simfil CONFIG REQUIRED)

add_executable(test_package src/example.cpp)
target_link_libraries(test_package simfil::simfil)
