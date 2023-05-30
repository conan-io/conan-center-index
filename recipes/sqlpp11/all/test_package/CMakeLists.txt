cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(Sqlpp11 CONFIG REQUIRED)

add_executable(${PROJECT_NAME} example.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
target_link_libraries(${PROJECT_NAME} sqlpp11::sqlpp11)
