cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(kickcat REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cc)
target_link_libraries(${PROJECT_NAME} PRIVATE kickcat::kickcat)
