cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(nvtx3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE nvtx3::nvtx3-c)
target_compile_features(${PROJECT_NAME}_c PRIVATE c_std_99)

add_executable(${PROJECT_NAME}_cxx test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cxx PRIVATE nvtx3::nvtx3-cpp)
