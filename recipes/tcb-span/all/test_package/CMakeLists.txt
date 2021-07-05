cmake_minimum_required(VERSION 3.1)

project(test_package)

find_package(tcb-span REQUIRED)

add_executable(test_package test_package.cxx)
target_link_libraries(test_package tcb-span::tcb-span)
