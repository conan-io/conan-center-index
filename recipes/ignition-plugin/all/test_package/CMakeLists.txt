cmake_minimum_required(VERSION 3.10)
project(test_package)

message(STATUS "---------------CMAKE BINARY DIR: ${CMAKE_BINARY_DIR}")

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
set(IGN_PLUGIN_MAJOR_VER "" CACHE STRING "Version of igition-plugin")

if(NOT IGN_PLUGIN_MAJOR_VER)
    message(FATAL_ERROR "IGN_PLUGIN_MAJOR_VER not set")
endif()

find_package(ignition-plugin${IGN_PLUGIN_MAJOR_VER} REQUIRED CONFIG)
find_package(ignition-cmake2 REQUIRED CONFIG)
find_package(DL)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-plugin${IGN_PLUGIN_MAJOR_VER}::ignition-plugin${IGN_PLUGIN_MAJOR_VER}-loader)
