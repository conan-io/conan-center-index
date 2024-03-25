cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(google-cloud-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} storage.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE google-cloud-cpp::storage)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
