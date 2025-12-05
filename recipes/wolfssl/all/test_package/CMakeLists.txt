cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(wolfssl REQUIRED CONFIG)

if (NOT CMAKE_SYSTEM_NAME MATCHES Generic)
    add_executable(${PROJECT_NAME} test_package.c)
else()
    add_library(${PROJECT_NAME} STATIC test_package.c)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE wolfssl::wolfssl)
