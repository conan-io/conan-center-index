cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)

find_package(azure-storage-cpp REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example azure-storage-cpp::azure-storage-cpp)
