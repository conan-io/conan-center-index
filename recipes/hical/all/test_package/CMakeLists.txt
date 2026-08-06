cmake_minimum_required(VERSION 3.20)
project(PackageTest CXX)

find_package(hical REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE hical::hical_core)
target_compile_features(example PRIVATE cxx_std_20)
