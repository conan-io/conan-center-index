cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(libnetfilter_log REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example libnetfilter_log::libnetfilter_log)