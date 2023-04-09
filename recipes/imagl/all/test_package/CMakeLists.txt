cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(imagl CONFIG REQUIRED)


add_executable(example example.cpp)
target_link_libraries(example imagl::imagl)
target_compile_features(example PRIVATE cxx_std_20)
