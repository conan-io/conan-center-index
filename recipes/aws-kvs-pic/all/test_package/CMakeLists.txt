cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBKVSPIC REQUIRED IMPORTED_TARGET libkvspic)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PkgConfig::LIBKVSPIC)
