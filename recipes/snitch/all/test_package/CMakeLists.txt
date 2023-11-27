cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(snitch REQUIRED CONFIG)

if (WITH_SHORTHAND)
    add_executable(standalone 200-standalone-with-shorthand.cpp)
else()
    add_executable(standalone 100-standalone.cpp)
endif()

if (HEADER_ONLY)
    target_compile_definitions(standalone PRIVATE HEADER_ONLY)
    target_link_libraries(standalone PRIVATE snitch::snitch-header-only)
else()
    target_link_libraries(standalone PRIVATE snitch::snitch)
endif()

target_compile_features(standalone PRIVATE cxx_std_20)
