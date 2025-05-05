cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(Orcania REQUIRED CONFIG)

option(ORCANIA_SHARED "Orcania is built as a shared library")

add_executable(${PROJECT_NAME} test_package.c)
if(ORCANIA_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE Orcania::Orcania)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE Orcania::Orcania-static)
endif()
