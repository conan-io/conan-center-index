cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(linuxdeploy CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package linuxdeploy::linuxdeploy) # Test packaging of includes and libs
target_compile_features(test_package PRIVATE cxx_std_14)

add_custom_command(TARGET test_package POST_BUILD 
    COMMAND linuxdeploy # Uses the linuxdeploy on PATH from buildenv
        --executable=$<TARGET_FILE:test_package> 
        --appdir AppDir 
        --create-desktop-file
        --icon-file=${CMAKE_CURRENT_SOURCE_DIR}/test_package.png 
    VERBATIM)
