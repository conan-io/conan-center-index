cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(serd REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package PRIVATE
        serd::serd
        )

set_target_properties(
        test_package PROPERTIES
        CXX_STANDARD 11
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
)
