cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(pybind11 REQUIRED CONFIG)

pybind11_add_module(test_package MODULE test_package.cpp)
