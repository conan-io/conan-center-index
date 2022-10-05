cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(octo-keygen-cpp CONFIG REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE octo-keygen-cpp::octo-keygen-cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
