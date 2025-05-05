cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(bx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED ON CXX_EXTENSIONS OFF)
target_link_libraries(${PROJECT_NAME} bx::bx)
