cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(enhex-generic_serialization REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example enhex-generic_serialization::enhex-generic_serialization)
set_target_properties(example PROPERTIES CXX_STANDARD 17)
