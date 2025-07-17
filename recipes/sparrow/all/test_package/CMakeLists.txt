cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(sparrow REQUIRED CONFIG)

add_executable(standalone main.cpp)

target_link_libraries(standalone PRIVATE sparrow::sparrow)
target_compile_features(standalone PRIVATE cxx_std_20)

set(SPARROW_VERSION_BEFORE_1 "${sparrow_VERSION}" VERSION_LESS "1.0.0")

target_compile_definitions(standalone PRIVATE SPARROW_VERSION_BEFORE_1=${SPARROW_VERSION_BEFORE_1})