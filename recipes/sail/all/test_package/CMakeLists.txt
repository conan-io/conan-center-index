cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(Sail REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_compile_definitions(test_package PRIVATE SAIL_DEMO_FILE_PATH="${CMAKE_CURRENT_SOURCE_DIR}/png.png")
target_link_libraries(test_package PRIVATE SAIL::sail)
