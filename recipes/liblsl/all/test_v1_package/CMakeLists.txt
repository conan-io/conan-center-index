cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(LSL CONFIG REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE LSL::lsl)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
