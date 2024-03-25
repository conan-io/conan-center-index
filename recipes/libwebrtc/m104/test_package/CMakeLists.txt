cmake_minimum_required(VERSION 3.2.0)
project(test_package CXX)

list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}")

find_package(libwebrtc REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)

target_link_libraries(${PROJECT_NAME} libwebrtc::libwebrtc)