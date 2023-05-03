cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(linux-headers-generic REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} linux-headers-generic)
