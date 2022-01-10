cmake_minimum_required(VERSION 3.12)

project(test_package VERSION 1.0.0 LANGUAGES CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
find_package(flatbush CONFIG REQUIRED)

add_executable(${PROJECT_NAME} "test_package.cpp")

target_link_libraries(${PROJECT_NAME} flatbush::flatbush)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
