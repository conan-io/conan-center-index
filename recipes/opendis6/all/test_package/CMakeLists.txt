cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(OpenDIS CONFIG REQUIRED)

add_executable(test_package_dis test_package.cpp)
target_link_libraries(test_package_dis PRIVATE OpenDIS::OpenDIS6)
set_target_properties(test_package_dis PROPERTIES CXX_STANDARD 14)
