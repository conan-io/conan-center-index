cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(blend2d CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package blend2d::blend2d)
target_compile_features(test_package PRIVATE cxx_std_11)
