cmake_minimum_required(VERSION 3.6)
project(test_package LANGUAGES CXX)

find_package(PkgConfig REQUIRED)
pkg_check_modules(CoinUtils REQUIRED IMPORTED_TARGET coinutils)
add_executable(${PROJECT_NAME}_pkgconfig test_package.cpp)
target_link_libraries(${PROJECT_NAME}_pkgconfig PRIVATE PkgConfig::CoinUtils)

find_package(coin-utils REQUIRED CONFIG)
add_executable(${PROJECT_NAME}_cmake test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cmake PRIVATE coin-utils::coin-utils)
