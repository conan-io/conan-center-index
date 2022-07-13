cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(beauty REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 20)
target_link_libraries(${CMAKE_PROJECT_NAME} beauty::beauty)
