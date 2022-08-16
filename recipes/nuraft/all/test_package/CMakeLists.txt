cmake_minimum_required(VERSION 3.11)
project(test_package LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(nuraft REQUIRED)

add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE test_package.cpp)
target_link_libraries(${PROJECT_NAME} nuraft::nuraft)
