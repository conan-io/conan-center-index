cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(gst-plugins-base REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE gst-plugins-base::gstreamer-plugins-base-1.0)
