cmake_minimum_required(VERSION 3.18)
project(test_package CXX)

find_package(ecbuild REQUIRED)

# ecBuild is primarily a set of CMake macros, let's just make sure we can include one
if(TARGET ecbuild::ecbuild)
    message(STATUS "ecbuild target exists (though typically we just use its macros)")
endif()

# We can also try including a macro
include(ecbuild_system)
message(STATUS "ecbuild_system included successfully")

add_executable(test_package test_package.cpp)
