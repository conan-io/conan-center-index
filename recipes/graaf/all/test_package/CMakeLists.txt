cmake_minimum_required(VERSION 3.11)
project(test_package LANGUAGES CXX)

find_package(graaflib REQUIRED CONFIG)

set(_CXX_STANDARD cxx_std_20)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE ${_CXX_STANDARD})
target_link_libraries(${PROJECT_NAME} PRIVATE Graaf::Graaf)
