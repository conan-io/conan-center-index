cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(Yder REQUIRED CONFIG)

option(YDER_SHARED "Yder is built as a shared library")

add_executable(${PROJECT_NAME} test_package.c)
if(YDER_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE Yder::Yder)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE Yder::Yder-static)
endif()
