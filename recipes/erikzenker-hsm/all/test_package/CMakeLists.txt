cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(hsm CONFIG REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(example example.cpp)
target_link_libraries(example hsm::hsm)
