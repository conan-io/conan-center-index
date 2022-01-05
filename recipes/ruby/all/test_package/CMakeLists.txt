cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(PkgConfig MODULE REQUIRED)
pkg_check_modules(ruby REQUIRED IMPORTED_TARGET ruby)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PkgConfig::ruby)

include(CTest)
add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
