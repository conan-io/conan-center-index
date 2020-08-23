cmake_minimum_required(VERSION 3.2.0)
project(test_package CXX)

# We set it only for the convenience of calling the executable
# in the package test function
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(absl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} main.cpp)
# Note: Conan 1.21 doesn't support granular target generation yet.
target_link_libraries(${PROJECT_NAME} absl::absl)
