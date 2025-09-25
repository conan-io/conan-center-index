cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(PCL REQUIRED surface CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE PCL::filters)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

# TODO: look into this (testing if this fixes test package on Windows, these flags are otherwise propagated by the upstream CMake scripts)
target_compile_definitions(${PROJECT_NAME} PRIVATE "__AVX2__")