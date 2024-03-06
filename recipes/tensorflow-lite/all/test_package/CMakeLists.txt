cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(tensorflowlite REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE tensorflow::tensorflowlite)
target_compile_features(test_package PRIVATE cxx_std_17)

if(CMAKE_SYSTEM_NAME MATCHES "Android")
  find_library(ANDROID_LOG_LIB log)
  target_link_libraries(test_package PRIVATE log)
endif()
