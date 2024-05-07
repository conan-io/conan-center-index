cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(libdb CONFIG REQUIRED)

add_executable(example src/test_package.c)
target_link_libraries(example libdb::libdb)
