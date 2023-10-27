cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(libipt REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_11 cxx_constexpr)
target_link_libraries(${PROJECT_NAME} libipt::libipt)
