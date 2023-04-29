cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(clickhouse-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE clickhouse-cpp-lib )

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
