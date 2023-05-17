cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(qtxlsxwriter REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qtxlsxwriter::qtxlsxwriter)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
# `fPIC` option must be used because qt was built with `reduce-relocations`
target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
