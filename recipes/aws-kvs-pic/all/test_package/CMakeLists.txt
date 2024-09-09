cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBKVSPIC REQUIRED IMPORTED_TARGET libkvspic)

add_executable(test_package test_package.c)
target_link_libraries(test_package PkgConfig::LIBKVSPIC)
