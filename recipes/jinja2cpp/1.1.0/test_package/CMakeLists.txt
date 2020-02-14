cmake_minimum_required(VERSION 2.8.0)
project(Jinja2CppTestPackage)

set(CMAKE_CXX_STANDARD 14)

find_package(jinja2cpp REQUIRED)

if (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    if (CMAKE_BUILD_TYPE MATCHES "Debug" AND MSVC_RUNTIME_TYPE)
        set (MSVC_RUNTIME_TYPE "${MSVC_RUNTIME_TYPE}d")
    endif ()

    set (CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} ${MSVC_RUNTIME_TYPE}")
    set (CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} ${MSVC_RUNTIME_TYPE}")
    set (CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} ${MSVC_RUNTIME_TYPE}")
    set (CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO "/PROFILE")

    message (STATUS "Build type: ${CMAKE_BUILD_TYPE}")
    message (STATUS "USE MSVC RUNTIME: ${MSVC_RUNTIME_TYPE}")

endif()

add_executable(jinja2cpp-test-package main.cpp)
target_link_libraries(jinja2cpp-test-package PRIVATE jinja2cpp::jinja2cpp)
