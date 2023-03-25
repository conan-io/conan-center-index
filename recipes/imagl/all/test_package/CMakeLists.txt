cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(imagl CONFIG REQUIRED)


add_executable(example example.cpp)
target_link_libraries(example imagl::imagl)
set_target_properties(example PROPERTIES CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON)
