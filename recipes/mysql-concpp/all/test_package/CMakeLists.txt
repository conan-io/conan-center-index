cmake_minimum_required(VERSION 3.30)
project(PackageTest CXX)

find_package(mysql-concpp REQUIRED CONFIG)
add_executable(example src/example.cpp)

target_link_libraries(example PRIVATE mysql::concpp)