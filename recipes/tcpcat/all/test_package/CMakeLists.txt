cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

add_executable(test_package test_package.cpp)

find_package(tcpcat CONFIG REQUIRED)
target_link_libraries(test_package tcpcat::tcpcat)
