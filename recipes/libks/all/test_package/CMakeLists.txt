cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libks2 CONFIG REQUIRED)



add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE libks2::libks2)
