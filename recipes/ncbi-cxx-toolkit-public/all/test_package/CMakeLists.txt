cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(ncbi-cxx-toolkit-public REQUIRED CONFIG)
add_executable(${PROJECT_NAME} basic_sample.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ncbi-cxx-toolkit-public::ncbi-cxx-toolkit-public)
