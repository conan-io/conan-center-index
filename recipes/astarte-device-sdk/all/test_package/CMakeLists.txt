cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(astarte_device_sdk REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE astarte_device_sdk::astarte_device_sdk)
