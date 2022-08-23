cmake_minimum_required(VERSION 3.15)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(wayland REQUIRED CONFIG)

add_executable(test_package ../test_package/test_package.c)
target_link_libraries(test_package PRIVATE wayland::wayland-client)
