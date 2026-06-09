cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(improc 1.0.3 CONFIG REQUIRED)
# improc's public headers include opencv2 headers; consumers must find OpenCV.
# For shared-library builds, CMakeDeps does not propagate transitive cmake configs,
# so we add include dirs directly without linking (improc already carries opencv at
# runtime for shared builds; linking here would cause duplicate symbols with static opencv).
find_package(OpenCV CONFIG REQUIRED)

add_executable(test_package src/test_package.cpp)
target_link_libraries(test_package PRIVATE improc::improc)
target_include_directories(test_package PRIVATE
    $<TARGET_PROPERTY:opencv::opencv,INTERFACE_INCLUDE_DIRECTORIES>)
