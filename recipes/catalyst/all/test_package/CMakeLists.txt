cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(catalyst REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PUBLIC catalyst::catalyst ${CMAKE_DL_LIBS})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

