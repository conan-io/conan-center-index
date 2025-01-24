cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(SDL3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} SDL3::SDL3)
