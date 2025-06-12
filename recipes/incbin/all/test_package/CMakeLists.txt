cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(incbin REQUIRED CONFIG)

# Verify that the helper tool is available when building with MSVC
# but we will not execute it to reduce complexity of test_package
if(MSVC)
    find_program(INCBIN_TOOL_PATH NAMES incbin_tool incbin_tool.exe REQUIRED)
endif()

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE incbin::incbin)
