cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(vtu11 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE vtu11::vtu11)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
