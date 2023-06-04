cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(re2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE re2::re2)
if (re2_VERSION VERSION_GREATER_EQUAL "20230602")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
