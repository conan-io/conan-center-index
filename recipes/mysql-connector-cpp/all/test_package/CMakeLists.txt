cmake_minimum_required(VERSION 3.15)
project(MySQLConnectorCPPTest CXX)

find_package(mysql-connector-cpp REQUIRED CONFIG)
add_executable(test_package src/test_package.cpp)
target_link_libraries(test_package mysql-connector-cpp::mysql-connector-cpp)
