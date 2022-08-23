cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(Metall REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package PRIVATE
        Metall::Metall
        )

set_target_properties(
        test_package PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
)
