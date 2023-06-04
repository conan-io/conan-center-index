cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(DataFrame REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE DataFrame::DataFrame)
if (DataFrame_VERSION VERSION_GREATER_EQUAL "2.1.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
