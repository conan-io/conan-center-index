cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
find_package(co REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cc)
target_link_libraries(${PROJECT_NAME} co::co)
