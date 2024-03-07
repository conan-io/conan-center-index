cmake_minimum_required(VERSION 3.15)
project(MySQLConnectorCPPTest CXX)

find_package(mysql-connector-cpp REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
# Config JDBC_ENABLED conditional
if (JDBC_ENABLED)
    target_compile_definitions(test_package PRIVATE USING_JDBC=1)
endif()
message("with JDBC IS " ${JDBC_ENABLED})

target_link_libraries(test_package mysql-connector-cpp::mysql-connector-cpp)
target_compile_features(test_package PRIVATE cxx_std_17)
