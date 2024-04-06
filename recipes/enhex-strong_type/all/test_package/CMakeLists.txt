cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(enhex-strong_type REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example enhex-strong_type::enhex-strong_type)
set_target_properties(example PROPERTIES CXX_STANDARD 17)
