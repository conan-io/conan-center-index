cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(hunspell REQUIRED CONFIG)

add_executable(test_package test_package.cxx)
target_link_libraries(test_package PRIVATE hunspell::hunspell)
