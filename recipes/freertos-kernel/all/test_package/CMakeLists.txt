cmake_minimum_required(VERSION 3.16)

project(test_package LANGUAGES C)

find_package(freertos-kernel REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(
  test_package PRIVATE freertos-kernel::freertos-kernel
)
