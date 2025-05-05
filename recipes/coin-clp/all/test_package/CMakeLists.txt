cmake_minimum_required(VERSION 3.6)
project(test_package LANGUAGES CXX)

find_package(PkgConfig REQUIRED)
pkg_check_modules(OsiClp REQUIRED IMPORTED_TARGET osi-clp)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::OsiClp)
