cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(octo-keygen-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} octo::octo-keygen-cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
