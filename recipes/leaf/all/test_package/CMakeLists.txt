cmake_minimum_required(VERSION 3.0)
project(test_package LANGUAGES CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(leaf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Boost::leaf)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
