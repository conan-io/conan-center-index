cmake_minimum_required(VERSION 3.1)

project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cpp-sort REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} cpp-sort-integrity.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} cpp-sort::cpp-sort)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 14)
