cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(naxp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp test_package_c.c)
target_link_libraries(${PROJECT_NAME} PRIVATE naxp::naxp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
