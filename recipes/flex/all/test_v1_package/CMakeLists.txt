cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)


include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(FLEX REQUIRED)

add_executable(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/basic_nr.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE FLEX::FLEX)
