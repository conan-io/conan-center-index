cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

if (CONAN_WAYLAND_LIBRARIES_ENABLED)
    find_package(wayland COMPONENTS wayland-client REQUIRED)
    add_executable(test_package test_package.c)
    target_link_libraries(test_package PRIVATE wayland::wayland-client)
endif()
