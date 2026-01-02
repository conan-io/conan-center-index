cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(intel_dfp REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE intel_dfp::intel_dfp)
