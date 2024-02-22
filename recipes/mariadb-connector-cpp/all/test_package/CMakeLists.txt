cmake_minimum_required(VERSION 3.15)
project(MariadbConnectorCPPTest CXX)

find_package(mariadb-connector-cpp REQUIRED CONFIG)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package mariadb-connector-cpp::mariadb-connector-cpp)
target_compile_features(test_package PRIVATE)
