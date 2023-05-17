cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(libdwarf REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libdwarf::libdwarf)

if(NOT libdwarf_VERSION MATCHES "^[0-9]*$")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "LIBDWARF_NEW_STRUCTURE")
endif()
