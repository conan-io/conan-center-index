cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(date REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE date::date)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(DATE_HEADER_ONLY)
    target_compile_definitions(${PROJECT_NAME} PRIVATE DATE_HEADER_ONLY)
endif()
