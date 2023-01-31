cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(sqlpp11-connector-sqlite3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE sqlpp11-connector-sqlite3::sqlpp11-connector-sqlite3)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
