cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(libusb REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE libusb::libusb)
