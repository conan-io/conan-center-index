cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 14)
endif()

find_package(restbed REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE restbed::restbed)
