cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(azure-storage-cpp REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example azure-storage-cpp::azure-storage-cpp)
target_compile_features(example PRIVATE cxx_std_11)
