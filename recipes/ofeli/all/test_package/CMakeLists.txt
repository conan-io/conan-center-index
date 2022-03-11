cmake_minimum_required(VERSION 3.4)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ofeli CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ofeli::ofeli)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
