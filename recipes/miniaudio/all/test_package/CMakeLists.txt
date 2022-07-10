cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(miniaudio REQUIRED)

add_executable(test_package example.c)
target_link_libraries(test_package miniaudio::miniaudio)
