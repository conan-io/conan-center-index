cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(transwarp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE transwarp::transwarp)
target_compile_definitions(${PROJECT_NAME} PRIVATE TRANSWARP_CPP11)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
