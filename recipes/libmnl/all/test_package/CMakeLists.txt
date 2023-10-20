cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(libmnl REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example libmnl::libmnl)
