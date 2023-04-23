cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(OpenBLAS CONFIG REQUIRED)
#find_package(OpenBLAS CONFIG COMPONENTS OpenBLAS::pthread REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} OpenBLAS::OpenBLAS)
