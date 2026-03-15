cmake_minimum_required(VERSION 3.28)
project(test_package)

find_package(beman.utf_view REQUIRED)

add_executable(test_package)
target_sources(test_package PRIVATE main.cpp)
target_link_libraries(test_package PRIVATE beman::utf_view)
