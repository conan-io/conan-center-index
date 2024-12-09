cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(libusb-compat REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
target_link_libraries(${CMAKE_PROJECT_NAME} libusb-compat::libusb-compat)
