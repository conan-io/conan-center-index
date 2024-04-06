cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(libdwarf REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libdwarf::libdwarf)

if(${libdwarf_VERSION} VERSION_LESS "0.9.1")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "LIBDWARF_NESTED_INCLUDE")
endif()
