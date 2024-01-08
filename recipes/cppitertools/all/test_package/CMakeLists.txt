cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(cppitertools REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cppitertools::cppitertools)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(ZIP_LONGEST)
    add_executable(test_zip_longest test_zip_longest.cpp)
    target_link_libraries(test_zip_longest PRIVATE cppitertools::cppitertools)
    target_compile_features(test_zip_longest PRIVATE cxx_std_17)
endif()
