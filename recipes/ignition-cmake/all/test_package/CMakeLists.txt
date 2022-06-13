cmake_minimum_required(VERSION 3.10.2)
project(test_package VERSION 1.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(IGN_CMAKE_VER "" CACHE STRING "Version of igition-cmake")

if(NOT IGN_CMAKE_VER)
    message(FATAL_ERROR "IGN_CMAKE_VER not set")
endif()

find_package(ignition-cmake${IGN_CMAKE_VER} REQUIRED COMPONENTS utilities)

ign_configure_project()
ign_configure_build()
