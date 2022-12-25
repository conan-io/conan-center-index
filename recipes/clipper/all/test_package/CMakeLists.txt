cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(clipper REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE clipper::clipper)
target_compile_definitions(${PROJECT_NAME} PRIVATE CLIPPER_MAJOR_VERSION=${CLIPPER_MAJOR_VERSION})
