cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(cli CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example cli::cli)

target_compile_features(example PRIVATE cxx_std_14)
