cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(QXlsx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} QXlsx::QXlsx)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
