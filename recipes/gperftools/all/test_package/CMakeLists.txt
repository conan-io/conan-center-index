cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(gperftools REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE gperftools::gperftools)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

add_executable(${PROJECT_NAME}_minimal test_package.cpp)
target_link_libraries(${PROJECT_NAME}_minimal PRIVATE gperftools::tcmalloc_minimal)
target_compile_features(${PROJECT_NAME}_minimal PRIVATE cxx_std_11)
