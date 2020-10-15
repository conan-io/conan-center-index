cmake_minimum_required(VERSION 3.5)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)

find_package(qt REQUIRED CONFIG)
find_package(karchive CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example karchive::karchive qt::qt)
