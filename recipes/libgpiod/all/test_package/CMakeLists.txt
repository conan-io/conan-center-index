cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(libgpiod REQUIRED)

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
target_link_libraries(${CMAKE_PROJECT_NAME} libgpiod::gpiod)
