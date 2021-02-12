cmake_minimum_required(VERSION 3.5)

project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)

target_compile_definitions(test_package PRIVATE flecs_STATIC)
target_link_libraries(test_package PRIVATE flecs_static)

set_target_properties(test_package PROPERTIES
        LINKER_LANGUAGE CXX
        CXX_STANDARD 11
        CXX_STANDARD_REQUIRED ON)
