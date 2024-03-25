cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(wayland COMPONENTS wayland-client REQUIRED)

# Test ECM FindWayland way
find_package(Wayland COMPONENTS Cursor REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE wayland::wayland-client Wayland::Cursor)
