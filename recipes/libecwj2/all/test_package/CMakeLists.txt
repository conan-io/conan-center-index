cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(libecwj2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libecwj2::libecwj2)

target_compile_definitions(${PROJECT_NAME} PRIVATE POSIX=1 LINUX=1 _GNU_SOURCE _REENTRANT _LARGEFILE64_SOURCE PATH_MAX=4096)
