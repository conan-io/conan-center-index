cmake_minimum_required(VERSION 3.6)
project(test_package LANGUAGES C)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libmariadb REQUIRED IMPORTED_TARGET libmariadb)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::libmariadb)
