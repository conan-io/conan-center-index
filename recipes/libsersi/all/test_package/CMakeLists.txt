cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(libsersi CONFIG REQUIRED)

add_executable(test_package_dis test_package.cpp)
target_link_libraries(test_package_dis PRIVATE libsersi::sersi)
set_target_properties(test_package_dis PROPERTIES CXX_STANDARD 14)
