cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(Python 3.8
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(test_package STABLE_ABI test_package.cpp)
