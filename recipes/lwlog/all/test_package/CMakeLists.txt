cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(lwlog CONFIG REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(example test_package.cpp)
target_link_libraries(example lwlog::lwlog_lib)
