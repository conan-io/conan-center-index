cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

#include(FindPkgConfig)
#pkg_check_modules(OsiCbc REQUIRED IMPORTED_TARGET osi-cbc)
#add_executable(${PROJECT_NAME}_pkgconfig test_package.cpp)
#target_link_libraries(${PROJECT_NAME}_pkgconfig PRIVATE PkgConfig::OsiCbc)

find_package(coin-cbc CONFIG REQUIRED)
add_executable(${PROJECT_NAME}_cmake test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cmake PRIVATE coin-cbc::coin-cbc)
