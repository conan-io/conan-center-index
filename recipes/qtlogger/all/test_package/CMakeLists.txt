cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES CXX)

find_package(qtlogger REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qtlogger::qtlogger)

set_target_properties(test_package PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)
