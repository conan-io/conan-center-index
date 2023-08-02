cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(pbtools REQUIRED CONFIG)

add_executable(test_package test_package.c hello_world.c)
target_link_libraries(test_package pbtools::pbtools)
