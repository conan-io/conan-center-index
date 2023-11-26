cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

include(FindPkgConfig)
# The transitive 'coinutils' is added explicitly to work around the linked library order otherwise being:
# OsiCbc CbcSolver Cbc bz2 z OsiCommonTests Osi Cgl ClpSolver Clp OsiClp CoinUtils
# which causes CoinUtils to not find bz2 and z symbols.
pkg_check_modules(OsiCbc REQUIRED IMPORTED_TARGET osi-cbc coinutils)
add_executable(${PROJECT_NAME}_pkgconfig test_package.cpp)
target_link_libraries(${PROJECT_NAME}_pkgconfig PRIVATE PkgConfig::OsiCbc)

find_package(coin-cbc CONFIG REQUIRED)
add_executable(${PROJECT_NAME}_cmake test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cmake PRIVATE coin-cbc::coin-cbc)
