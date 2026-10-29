cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(fmi-ls-bus REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fmi-ls-bus::fmi-ls-bus)
