cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(PkgConfig REQUIRED)
pkg_check_modules(CAP REQUIRED IMPORTED_TARGET libcap)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::CAP)
