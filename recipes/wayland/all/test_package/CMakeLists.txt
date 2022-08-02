cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(wayland COMPONENTS wayland-client REQUIRED)
find_program(WAYLAND_SCANNER wayland-scanner)
if (NOT WAYLAND_SCANNER)
    message(FATAL_ERROR "Could not find wayland-scanner executable")
endif()

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE wayland::wayland-client)
