cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(picojson REQUIRED)

add_executable(example example.cpp)
set_property(TARGET example PROPERTY CXX_STANDARD 11)

target_link_libraries(example picojson::picojson)
