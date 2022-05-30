cmake_minimum_required(VERSION 3.12)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(fpgen REQUIRED CONFIG)

add_executable(${PROJECT_NAME} main.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
target_link_libraries(${PROJECT_NAME} fpgen::fpgen)
