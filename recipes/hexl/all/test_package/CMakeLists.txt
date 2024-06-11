cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Hexl REQUIRED CONFIG)

find_package(Hexl COMPONENTS hexl REQUIRED)
add_executable(example example.cpp)
target_link_libraries(example PRIVATE Hexl::hexl)

