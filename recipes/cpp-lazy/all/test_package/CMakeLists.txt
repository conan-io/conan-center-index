cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(cpp-lazy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cpp-lazy::cpp-lazy)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(cpp-lazy_VERSION VERSION_GREATER_EQUAL "8.0.0")
    find_package(fmt REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
endif()

