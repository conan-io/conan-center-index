cmake_minimum_required(VERSION 3.22)
project(test_package LANGUAGES C CXX)

find_package(box3d REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_link_libraries(${PROJECT_NAME} PRIVATE box3d::box3d)
