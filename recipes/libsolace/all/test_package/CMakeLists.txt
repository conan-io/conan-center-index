cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libsolace REQUIRED CONFIG)

set(CMAKE_CXX_STANDARD_REQUIRED on)

add_executable(example example.cpp)

# libsolace requires at least C++17
set_target_properties(example PROPERTIES CXX_STANDARD 17)
target_link_libraries(example libsolace::libsolace)
