cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(wayland REQUIRED CONFIG)
find_program(WAYLAND_SCANNER_EXECUTABLE NAMES wayland-scanner REQUIRED)


add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(test_package PRIVATE wayland::wayland-client)
