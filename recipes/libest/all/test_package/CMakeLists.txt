cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(libest REQUIRED CONFIG)

add_executable(example example.c)
target_link_libraries(example PRIVATE libest::libest)
