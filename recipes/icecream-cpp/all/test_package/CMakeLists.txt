cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(icecream-cpp REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE icecream-cpp::icecream-cpp)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
