cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(stx REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE stx::stx)
