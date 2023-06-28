cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(mattiasgustavsson-libs REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE mattiasgustavsson-libs::mattiasgustavsson-libs)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
