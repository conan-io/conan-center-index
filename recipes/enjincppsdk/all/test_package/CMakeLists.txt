cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(enjinsdk REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} enjinsdk::enjinsdk)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
