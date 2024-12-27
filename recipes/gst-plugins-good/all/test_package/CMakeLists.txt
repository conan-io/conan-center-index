cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(gst-plugins-good CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} gst-plugins-good::gst-plugins-good)
