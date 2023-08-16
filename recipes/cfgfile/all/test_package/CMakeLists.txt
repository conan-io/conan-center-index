cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(cfgfile REQUIRED CONFIG)

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp"
    COMMAND cfgfile.generator -i "${CMAKE_CURRENT_SOURCE_DIR}/session_cfg.conf" -o "${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/session_cfg.conf"
)

add_executable(${PROJECT_NAME} test_package.cpp "${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp")
target_link_libraries(${PROJECT_NAME} PRIVATE cfgfile::cfgfile)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
