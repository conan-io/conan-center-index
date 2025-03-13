cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(Python 3.8 REQUIRED COMPONENTS Development)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(test_package NB_STATIC test_package.cpp)
