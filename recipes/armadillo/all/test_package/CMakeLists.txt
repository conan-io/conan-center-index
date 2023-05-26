cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(armadillo CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example armadillo::armadillo)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
