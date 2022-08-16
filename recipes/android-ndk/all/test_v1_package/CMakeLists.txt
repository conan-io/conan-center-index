cmake_minimum_required(VERSION 3.0)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME})
