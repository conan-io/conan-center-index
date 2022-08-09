cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(blend2d CONFIG REQUIRED)

set(CMAKE_VERBOSE_MAKEFILE ON)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE blend2d::blend2d)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
