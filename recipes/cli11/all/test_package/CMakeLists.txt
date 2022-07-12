cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(CLI11 REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${CMAKE_PROJECT_NAME} CLI11::CLI11)
