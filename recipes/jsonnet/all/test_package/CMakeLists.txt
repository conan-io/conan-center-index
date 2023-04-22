cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C CXX)

find_package(jsonnet CONFIG REQUIRED)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE jsonnet::libjsonnet)

add_executable(${PROJECT_NAME}_cxx test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cxx PRIVATE jsonnet::libjsonnetpp)
if(jsonnet_VERSION VERSION_LESS "0.20.0")
    target_compile_features(${PROJECT_NAME}_cxx PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME}_cxx PRIVATE cxx_std_17)
endif()
