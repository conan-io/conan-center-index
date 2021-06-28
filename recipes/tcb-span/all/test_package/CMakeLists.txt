cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(tcb-span REQUIRED)

add_executable(test_package test_package.cxx)
target_link_libraries(test_package tcb-span::tcb-span)
