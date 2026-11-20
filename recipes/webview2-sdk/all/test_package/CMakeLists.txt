cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(webview2-sdk CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE webview2-sdk::webview2-sdk)
