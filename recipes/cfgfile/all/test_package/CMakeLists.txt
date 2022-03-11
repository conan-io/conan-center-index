cmake_minimum_required(VERSION 3.1)

project(cfgfile.test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

conan_basic_setup(TARGETS)

find_package(cfgfile REQUIRED)

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp"
    COMMAND cfgfile.generator -i "${CMAKE_CURRENT_SOURCE_DIR}/session_cfg.conf" -o "${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/session_cfg.conf"
)

include_directories(${CMAKE_CURRENT_BINARY_DIR})

add_executable(${PROJECT_NAME}
    example.cpp
    "${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp"
)

target_link_libraries(${PROJECT_NAME} cfgfile::cfgfile)

set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
