cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(AWSSDK REQUIRED CONFIG)

add_subdirectory(aws-sdk-cpp-plugin)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} aws-sdk-cpp-plugin)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
