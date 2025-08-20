cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(xorg REQUIRED CONFIG)
find_package(vaapi REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE vaapi::vaapi xorg::xorg)

find_package(PkgConfig REQUIRED)
pkg_check_modules(PC_LIBVA REQUIRED libva)
message(STATUS "libva .pc version: ${PC_LIBVA_VERSION}")
