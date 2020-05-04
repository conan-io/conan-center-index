cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)


add_executable(example example.cpp)
target_compile_definitions(example PRIVATE BUILD_DIR="${CMAKE_CURRENT_BINARY_DIR}")