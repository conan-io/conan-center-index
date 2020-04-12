cmake_minimum_required(VERSION 3.1.2)
project(PackageTest CXX)

find_package(libdxfrw)

set(CMAKE_CXX_STANDARD 11)

add_executable(example example.cpp)
target_link_libraries(example libdxfrw::libdxfrw)

